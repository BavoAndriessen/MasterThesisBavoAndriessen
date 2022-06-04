package manual

import (
	"github.com/spf13/cobra"
	"k8s.io/klog/v2"
)

func Inject(filename string, outputfilename string) (err error) {

	//var reader io.Reader
	//var inputFile = os.Stdin
	//if filename == "-" {
	//	reader = bufio.NewReader(os.Stdin)
	//}
	//if inputFile, err = os.Open(filename); err != nil {
	//	return err
	//}
	//reader = inputFile
	//defer func() {
	//	if errClose := inputFile.Close(); errClose != nil {
	//		_ = fmt.Errorf("Error: close file from %s, %s", filename, errClose)
	//		err = errClose
	//	}
	//}()

	//var writer io.Writer
	//if outputfilename == "" {
	//	writer = os.Stdout
	//} else {
	//	var out *os.File
	//	if out, err = os.Create(outputfilename); err != nil {
	//		return err
	//	}
	//	writer = out
	//	defer func() {
	//		if errClose := out.Close(); errClose != nil {
	//			_ = fmt.Errorf("Error: close file from %s, %s", outputfilename, errClose)
	//			err = errClose
	//		}
	//	}()
	//}

	//text, _ = reader.ReadString('\n')

	//b := make([]byte, 8)
	//err = nil
	//for {
	//	n, err := reader.Read(b)
	//	fmt.Printf("n = %v err = %v b = %v\n", n, err, b)
	//	fmt.Printf("b[:n] = %q\n", b[:n])
	//	if err == io.EOF {
	//		break
	//	}
	//}

	return err
}

var (
	sidecarImage   string
	outputfilename string
)

var CmdManual = &cobra.Command{
	Use:   "manual [OPTIONS] <configration file>",
	Short: "Manually inject a deucalion sidecar into a pod",
	Long:  `Given a pod specification, this command injects a sidecar into the pod. It does so by reading on the file and adding a container to the pod object.`,
	Args:  cobra.MinimumNArgs(1),
	Run:   main,
}

func init() {
	CmdManual.Flags().StringVar(&sidecarImage, "sidecar-image", "",
		"Image to be used as the injected sidecar")
	CmdManual.Flags().StringVar(&outputfilename, "outputfile-name", "", "Output file to write output to, if not specified output to stdout")
	CmdManual.MarkFlagRequired("sidecar-image")
}

func main(cmd *cobra.Command, args []string) {
	klog.Info("TODO")
	//Inject(args[0], outputfilename)
}
