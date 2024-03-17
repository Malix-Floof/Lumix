#!/bin/bash

echo """
  ██╗     ██╗   ██╗███╗   ███╗██╗██╗  ██╗    ██╗   ██╗██████╗    ███████╗
  ██║     ██║   ██║████╗ ████║██║╚██╗██╔╝    ██║   ██║╚════██╗   ╚════██║
  ██║     ██║   ██║██╔████╔██║██║ ╚███╔╝     ██║   ██║ █████╔╝       ██╔╝
  ██║     ██║   ██║██║╚██╔╝██║██║ ██╔██╗     ╚██╗ ██╔╝ ╚═══██╗      ██╔╝ 
  ███████╗╚██████╔╝██║ ╚═╝ ██║██║██╔╝ ██╗     ╚████╔╝ ██████╔╝██╗   ██║  
  ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═╝      ╚═══╝  ╚═════╝ ╚═╝   ╚═╝  
"""

echo "Welcome to Lumix v3.7 startup script!"
echo "if you have questions join our support Discord server - discord.gg/SpTBwz4xsa"

distro=$(lsb_release -si)

if [ -e ./lenv ]; then
    echo " "
    echo "Launching venv..."
    source ./lenv/bin/activate
    echo "Venv launched!"
    echo "Launching bot..."
    python3 ./bot.py
    echo "Bot launched!"
else
    if command -v rpm &> /dev/null; then
        if rpm -q python3 &> /dev/null; then
            echo " "
            echo "Bot is not configured..."
            echo -n "Install using venv? (ONLY VENV) [Y/n]: "
            read -r key
            if [[ $key == "n" || $key == "N" ]]; then
                echo "Exiting script..."
                exit 1
            elif [[ $key == "Y" || $key == "y" || $key == "" ]]; then
                python3 -m venv lenv
                source lenv/bin/activate
                if [[ -f "requirements.txt" ]]; then
                    pip install -r requirements.txt
                    pip install git+https://github.com/DisnakeCommunity/disnake-ext-components.git
                else
                    echo "Error: requirements.txt not found. Please make sure the file exists."
                    exit 1
                fi
                echo "Close the script and configure the bot parameters in config.py"
                read -r -p "Press Enter to continue..."
                exit 0
            fi
        fi
    elif command -v pacman &> /dev/null; then
        if pacman -Q python3 &> /dev/null; then
            echo " "
            echo "Bot is not configured..."
            echo -n "Install using venv? (ONLY VENV) [Y/n]: "
            read -r key
            if [[ $key == "n" || $key == "N" ]]; then
                echo "Exiting script..."
                exit 1
            elif [[ $key == "Y" || $key == "y" || $key == "" ]]; then
                python3 -m venv lenv
                source lenv/bin/activate
                if [[ -f "requirements.txt" ]]; then
                    pip install -r requirements.txt
                    pip install git+https://github.com/DisnakeCommunity/disnake-ext-components.git
                else
                
                    echo "Error: requirements.txt not found. Please make sure the file exists."
                    exit 1
                fi
                echo "Close the script and configure the bot parameters in config.py"
                read -r -p "Press Enter to continue..."
                exit 0
            fi
        fi
    elif command -v dpkg &> /dev/null; then
        if dpkg -l python3 &> /dev/null; then
            echo " "
            echo "Bot is not configured..."
            echo -n "Install using venv? (ONLY VENV) [Y/n]: "
            read -r key
            if [[ $key == "n" || $key == "N" ]]; then
                echo "Exiting script..."
                exit 1
            elif [[ $key == "Y" || $key == "y" || $key == "" ]]; then
                python3 -m venv lenv
                source lenv/bin/activate
                if [[ -f "requirements.txt" ]]; then
                    pip install -r requirements.txt
                    pip install git+https://github.com/DisnakeCommunity/disnake-ext-components.git
                else
                    echo "Error: requirements.txt not found. Please make sure the file exists."
                    exit 1
                fi
                echo "Close the script and configure the bot parameters in config.py"
                read -r -p "Press Enter to continue..."
                exit 0
            fi
        fi
    else
        echo " "
        echo "Python is not installed. Install Python version 3.11.7 using your package manager"
        exit 1
    fi
fi
