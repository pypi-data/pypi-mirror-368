---
mode: agent
---
# Debugging failed requests to MSODS on OneBox

This guide describes the steps to obtain an insight into failed requests, recorded in a log file.

## Goal
The goal is to find all log entries related to a specific correlation ID within a specified time window, and to filter those entries to only include lines that contain an "ErrorCode". Afterwards, any stack traces related to those errors should be extracted for further analysis. Ideally, we want to identify the root cause of the failure.

## Prerequisites
- WinRM installed and configured on the target server.
- WinRM MCP server installed and configured to execute commands on the target server.

## Required Information
- **Correlation ID**: A unique identifier for the request that failed, e.g. GUID "ffffffff-ffff-ffff-ffff-ffffffffffff".
  - This ID is typically found in the error message or logs related to the failed request.
  - It is used to trace the request through the system and find all related log entries.
- **Target Time**: The time in UTC when the request was made, which will help narrow down the search for relevant log entries.
  - The script will use this time to filter log entries within a specific time window.

## Instructions
1. collect the correlation ID and the target time in UTC format.
2. run the following PowerShell script on the target server to find all log entries related to the correlation ID within a specified time window. 
   Adjust the parameters as needed:
   - `<correlation-id>`: The correlation ID to search for (e.g. "ffffffff-ffff-ffff-ffff-ffffffffffff").
   - `<datetime-in-utc>`: The target time in UTC format `YYYY-MM-DD HH:MM:SS` (e.g. "2023-10-01 12:00:00").
   Keep in mind that the script will be executed remotely, so ensure efficient implementation of the script to avoid performance issues.
```powershell
param(
    [string]$CorrelationId = "<correlation-id>",
    [DateTime]$TargetTime = [DateTime]"<datetime-in-utc>",
    [int]$WindowHours = 1,
    [string]$LogPath = "D:\Office12.0\SHARED\ULSLOGS\Monitoring"
)

# Get all log files and filter by time window
$allFiles = Get-ChildItem -Path $LogPath -Filter "*.log" -File
$relevantFiles = $allFiles | Where-Object { 
    [Math]::Abs(($_.LastWriteTime - $TargetTime).TotalHours) -le $WindowHours 
}

if ($relevantFiles.Count -eq 0) {
    Write-Host "No files found within the specified time window!"
    return
}

# Process each relevant file and output matching lines
foreach ($file in $relevantFiles) {
    $matches = Select-String -Path $file.FullName -Pattern $CorrelationId -AllMatches
    
    if ($matches) {
        foreach ($match in $matches) {
            # Only output lines that contain both correlation ID and "ErrorCode"
            if ($match.Line -match "ErrorCode") {
                Write-Host "$($file.Name):$($match.LineNumber): $($match.Line)"
            }
        }
    }
}
```

3. After running the script, review the output for any relevant stack traces or error messages that can help identify the root cause of the failure.
4. If stack traces are found, you can extract them for further analysis. You may want to save the output to a file for easier review
5. Summarize the findings and document any potential root causes or next steps for resolution.
   Make sure the output contains:
   - the root cause of the failure
   - (if applicable) any relevant stack traces, including the file name and line number where the error occurred
   - any input and context that led to the failure (e.g. HTTP request details, user actions, etc.)
   - any additional context that may help in understanding the issue