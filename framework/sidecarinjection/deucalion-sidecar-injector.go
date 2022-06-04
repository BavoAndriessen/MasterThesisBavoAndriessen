package main

import (
	"bavoandriessen/deucalion-sidecar-injector/manual"
	"bavoandriessen/deucalion-sidecar-injector/webhook"
	"github.com/spf13/cobra"
	"k8s.io/component-base/cli"
	"os"
)

var Version = "development"

func main() {
	rootCmd := &cobra.Command{
		Use:     "deucalion-sidecar-injector",
		Version: Version,
	}
	rootCmd.AddCommand(webhook.CmdWebhook)
	rootCmd.AddCommand(manual.CmdManual)
	code := cli.Run(rootCmd)
	os.Exit(code)
}
