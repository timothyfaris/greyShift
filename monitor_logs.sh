#!/bin/bash
# greyShift Docker Log Monitor
# This script helps you monitor the greyShift application logs in real-time

echo "greyShift Log Monitor"
echo "====================="
echo ""

show_menu() {
    echo -e "\e[33mSelect an option:\e[0m"
    echo "1. View live logs (all activity)"
    echo "2. View processing events only"
    echo "3. View user activity (visits and downloads)"
    echo "4. View errors and warnings only"
    echo "5. View last 20 log entries"
    echo "6. Monitor processing performance"
    echo "7. Exit"
    echo ""
}

while true; do
    show_menu
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            echo -e "\e[36mViewing live logs (press Ctrl+C to stop)...\e[0m"
            docker-compose logs -f
            ;;
        2)
            echo -e "\e[36mViewing processing events only (press Ctrl+C to stop)...\e[0m"
            docker-compose logs -f | grep "Processing"
            ;;
        3)
            echo -e "\e[36mViewing user activity (press Ctrl+C to stop)...\e[0m"
            docker-compose logs -f | grep -E "(Page visit|Download)"
            ;;
        4)
            echo -e "\e[36mViewing errors and warnings only (press Ctrl+C to stop)...\e[0m"
            docker-compose logs -f | grep -E "(ERROR|WARNING)"
            ;;
        5)
            echo -e "\e[36mLast 20 log entries:\e[0m"
            docker-compose logs --tail 20
            ;;
        6)
            echo -e "\e[36mRecent processing performance:\e[0m"
            docker-compose logs | grep "Processing completed" | tail -10
            ;;
        7)
            echo -e "\e[33mExiting...\e[0m"
            exit 0
            ;;
        *)
            echo -e "\e[31mInvalid choice. Please select 1-7.\e[0m"
            ;;
    esac
    
    if [ "$choice" != "7" ]; then
        echo ""
        read -p "Press Enter to continue..."
        clear
    fi
done