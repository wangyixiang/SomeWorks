package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

func main() {
	resize := 100
	lowshotDir := `D:\\datasets\\lowshot\\TrainData_Base_100x100`
	lowshotDirResized := fmt.Sprintf(`C:\\dataset\\lowshot\\TrainData_Base_%dx%d`, resize, resize)
	sizestr := fmt.Sprintf("%dx%d", resize, resize)
	subdirs, _ := ioutil.ReadDir(lowshotDir)
	var wg sync.WaitGroup
	goroutineChan := make(chan int, 10)

	for _, dir := range subdirs {
		wg.Add(1)
		goroutineChan <- 1
		go func(dirInfo os.FileInfo) {
			var srcFilename, dstFilename string
			files, _ := ioutil.ReadDir(filepath.Join(lowshotDir, dirInfo.Name()))
			for _, file := range files {
				if strings.Contains(file.Name(), sizestr) {
					if _, err := os.Stat(filepath.Join(lowshotDirResized, dirInfo.Name())); err != nil {
						err = os.Mkdir(filepath.Join(lowshotDirResized, dirInfo.Name()), 0775)
					}
					srcFilename = filepath.Join(lowshotDir, dirInfo.Name(), file.Name())
					dstFilename = filepath.Join(lowshotDirResized, dirInfo.Name(), file.Name())
					if err := os.Rename(srcFilename, dstFilename); err != nil {
						fmt.Println(err)
					}
				}
			}
			<-goroutineChan
			wg.Done()
		}(dir)
	}

	wg.Wait()
}

func copyFile(src, dst string) (err error) {
	in, err := os.Open(src)
	if err != nil {
		return
	}
	defer in.Close()

	out, err := os.Create(dst)
	if err != nil {
		return
	}

	defer func() {
		cerr := out.Close()
		if err == nil {
			err = cerr
		}
	}()

	if _, err = io.Copy(out, in); err != nil {
		return
	}

	err = out.Sync()
	return
}
