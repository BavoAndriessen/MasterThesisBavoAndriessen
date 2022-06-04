/*
Copyright 2018 The Kubernetes Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package webhook

import (
	"fmt"
	v1 "k8s.io/api/admission/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/klog/v2"
)

const (
	deucalionSidecarServiceAccountEnvVarsAndConfigMapPatch string = `[
			{"op":"add", "path":"/spec/volumes/-", "value": {"name": "deucalion-config-volume", "configMap": {"name": "%v"}}},
			{"op":"add", "path":"/spec/containers/-","value":{"image":"%v","name":"deucalion-sidecar", "env": [{"name": "DEUCALION_ALERT_NAME", "value": "%v"}, {"name": "DEUCALION_ALERT_MANAGER_HOST", "value": "%v"}, {"name": "DEUCALION_ALERT_MANAGER_PORT", "value": "%v"}] , "resources":{}, "volumeMounts": [{"name": "deucalion-config-volume", "mountPath": "/etc/deucalion", "readOnly": true}]}},
			{"op":"add", "path": "/spec/automountServiceAccountToken", "value": true},
			{"op":"add", "path": "/spec/serviceAccountName", "value": "%v"}
		]`
)

func mutatePodsSidecar(ar v1.AdmissionReview) *v1.AdmissionResponse {
	shouldPatchPod := func(pod *corev1.Pod) bool {
		return !hasContainer(pod.Spec.Containers, "deucalion-sidecar")
	}
	return applyPodPatch(ar, shouldPatchPod, deucalionSidecarServiceAccountEnvVarsAndConfigMapPatch)
}

func hasContainer(containers []corev1.Container, containerName string) bool {
	for _, container := range containers {
		if container.Name == containerName {
			return true
		}
	}
	return false
}

func applyPodPatch(ar v1.AdmissionReview, shouldPatchPod func(*corev1.Pod) bool, patch string) *v1.AdmissionResponse {
	klog.V(2).Info("mutating pods")
	podResource := metav1.GroupVersionResource{Group: "", Version: "v1", Resource: "pods"}
	if ar.Request.Resource != podResource {
		klog.Errorf("expect resource to be %s", podResource)
		return nil
	}

	raw := ar.Request.Object.Raw
	pod := corev1.Pod{}
	deserializer := codecs.UniversalDeserializer()
	if _, _, err := deserializer.Decode(raw, nil, &pod); err != nil {
		klog.Error(err)
		return toV1AdmissionResponse(err)
	}

	preferredSidecarImage := sidecarImage
	if preferred, ok := pod.Annotations["deucalion-sidecar-image"]; ok {
		preferredSidecarImage = preferred
	}

	var userDefinedConfigMapName string
	if configMapName, ok := pod.Annotations["deucalion-config-map"]; ok {
		userDefinedConfigMapName = configMapName
	} else {
		klog.Error("deucalion-config-map annotation not set! Not allowing pod creation. ")
		return &v1.AdmissionResponse{
			Allowed: false,
			Result: &metav1.Status{
				Status:  "Failure",
				Message: "deucalion-config-map pod annotation not set. ",
				Code:    500,
			},
		}
	}

	if preferredSidecarImage == "" {
		klog.Error("No sidecar provided in arguments, not creating pod. ")
		return &v1.AdmissionResponse{
			Allowed: false,
			Result: &metav1.Status{
				Status:  "Failure",
				Message: "No image specified by the sidecar-image parameter",
				Code:    500,
			},
		}
	}

	// TODO: controleren of alle annotaties aanwezig zijn om een deucalion sidecar te injecteren

	klog.Info("Injecting " + preferredSidecarImage + " into " + pod.GenerateName)

	reviewResponse := v1.AdmissionResponse{}
	reviewResponse.Allowed = true
	if shouldPatchPod(&pod) {
		reviewResponse.Patch = []byte(fmt.Sprintf(patch, userDefinedConfigMapName, preferredSidecarImage, alertManagerAlertName, alertManagerHost, alertManagerPort, serviceAccountName))
		pt := v1.PatchTypeJSONPatch
		reviewResponse.PatchType = &pt
	}
	return &reviewResponse
}
