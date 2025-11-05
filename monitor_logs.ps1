# greyShift Docker Log Monitor
# This script helps you monitor the greyShift application logs in real-time

Write-Host "greyShift Log Monitor" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""

# Function to display menu
function Show-Menu {
    Write-Host "Select an option:" -ForegroundColor Yellow
    Write-Host "1. View live logs (all activity)"
    Write-Host "2. View processing events only"
    Write-Host "3. View user activity (visits and downloads)"
    Write-Host "4. View errors and warnings only"
    Write-Host "5. View last 20 log entries"
    Write-Host "6. Monitor processing performance"
    Write-Host "7. Exit"
    Write-Host ""
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-7)"
    
    switch ($choice) {
        "1" {
            Write-Host "Viewing live logs (press Ctrl+C to stop)..." -ForegroundColor Cyan
            docker-compose logs -f
        }
        "2" {
            Write-Host "Viewing processing events only (press Ctrl+C to stop)..." -ForegroundColor Cyan
            docker-compose logs -f | Select-String "Processing"
        }
        "3" {
            Write-Host "Viewing user activity (press Ctrl+C to stop)..." -ForegroundColor Cyan
            docker-compose logs -f | Select-String "(Page visit|Download)"
        }
        "4" {
            Write-Host "Viewing errors and warnings only (press Ctrl+C to stop)..." -ForegroundColor Cyan
            docker-compose logs -f | Select-String "(ERROR|WARNING)"
        }
        "5" {
            Write-Host "Last 20 log entries:" -ForegroundColor Cyan
            docker-compose logs --tail 20
        }
        "6" {
            Write-Host "Recent processing performance:" -ForegroundColor Cyan
            docker-compose logs | Select-String "Processing completed" | Select-Object -Last 10
        }
        "7" {
            Write-Host "Exiting..." -ForegroundColor Yellow
            exit
        }
        default {
            Write-Host "Invalid choice. Please select 1-7." -ForegroundColor Red
        }
    }
    
    if ($choice -ne "7") {
        Write-Host ""
        Write-Host "Press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Clear-Host
    }
    
} while ($choice -ne "7")