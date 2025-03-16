###########################################
# Script Name : Directory Parser 
# Description : This script recursively scans a shared directory and deletes files 
# that do not match the specified extensions. It uses error handling 
# and logging to ensure stability and proper execution.
###########################################


# Define the network share path and root directory
$sharePath = "\\HOSTNAME\C$\share\DataTransfers"
$rootDirectory = "transfers"

# List of allowed file extensions (files not matching these will be deleted)
$extensionsToKeep = @("txt", "pdf")

# Function to process files within a directory
function ProcessFilesInDirectory {
    param (
        [string]$directoryPath  # Directory path to scan for files
    )

    # Check if the directory exists before processing
    if (!(Test-Path -Path $directoryPath)) {
        Write-Warning "Directory does not exist: $directoryPath"
        return
    }

    # Get a list of files in the directory
    $files = Get-ChildItem -Path $directoryPath -File -ErrorAction SilentlyContinue

    # Check if the directory contains files
    if ($files.Count -eq 0) {
        Write-Output "No files found in: $directoryPath."
        return
    }

    Write-Output "Processing $($files.Count) files in: $directoryPath."

    # Iterate through each file in the directory
    foreach ($file in $files) {
        $extension = $file.Extension.TrimStart('.').ToLower()  # Normalize file extension

        # Check if the file extension is in the allowed list
        if ($extensionsToKeep -contains $extension) {
            Write-Output "Keeping: $($file.Name)"  # Log kept files
        } else {
            try {
                # Attempt to delete the file
                Remove-Item -Path $file.FullName -Force -ErrorAction Stop
                Write-Output "Deleted: $($file.Name)"
            } catch {
                # Log any errors encountered during deletion
                Write-Warning "Failed to delete: $($file.Name) - $($_.Exception.Message)"
            }
        }
    }

    Write-Output "File processing complete for: $directoryPath."
}

# Function to process a directory and its subdirectories
function ProcessDirectory {
    param (
        [string]$directoryPath  # Directory path to process
    )

    # Ensure the directory exists before proceeding
    if (!(Test-Path -Path $directoryPath)) {
        Write-Warning "Skipping non-existent directory: $directoryPath"
        return
    }

    # Process files in the current directory
    ProcessFilesInDirectory -directoryPath $directoryPath

    # Get all subdirectories within the current directory
    $subdirectories = Get-ChildItem -Path $directoryPath -Directory -ErrorAction SilentlyContinue

    # Recursively process each subdirectory
    foreach ($subdirectory in $subdirectories) {
        ProcessDirectory -directoryPath $subdirectory.FullName
    }
}

# Construct the full path for processing
$fullPath = Join-Path -Path $sharePath -ChildPath $rootDirectory

# Validate the root directory and begin processing
if (Test-Path -Path $fullPath) {
    Write-Output "Starting directory processing at: $fullPath"
    ProcessDirectory -directoryPath $fullPath
} else {
    Write-Warning "Root directory does not exist: $fullPath"
}
