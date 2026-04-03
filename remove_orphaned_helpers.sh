#!/bin/bash

# Script to remove orphaned PrivilegedHelperTools and associated files
# Run with: bash remove_orphaned_helpers.sh

echo "This script will remove orphaned helper tools and their associated files."
echo "You will be prompted for your password to execute sudo commands."
echo ""
echo "The following will be removed:"
echo "  - Google Drive Icon Helper (2014)"
echo "  - BBEdit helper (com.barebones.authd)"
echo "  - Old Microsoft Office licensing helper (2010)"
echo "  - CleanMyMac3 Agent (superseded by CleanMyMac4)"
echo "  - Telestream licensing helper"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Step 1: Unloading launch services..."

# Unload CleanMyMac3 user scheduler
if launchctl list | grep -q "com.macpaw.CleanMyMac3.Scheduler"; then
    echo "Unloading CleanMyMac3 scheduler..."
    launchctl unload ~/Library/LaunchAgents/com.macpaw.CleanMyMac3.Scheduler.plist 2>/dev/null
fi

# Unload system daemons (these may not be loaded, but try anyway)
echo "Unloading system daemons (if loaded)..."
sudo launchctl unload /Library/LaunchDaemons/com.barebones.authd.plist 2>/dev/null
sudo launchctl unload /Library/LaunchDaemons/com.macpaw.CleanMyMac3.Agent.plist 2>/dev/null
sudo launchctl unload /Library/LaunchDaemons/com.microsoft.office.licensing.helper.plist 2>/dev/null
sudo launchctl unload /Library/LaunchDaemons/net.telestream.LicensingHelper.plist 2>/dev/null

echo ""
echo "Step 2: Removing LaunchAgents/LaunchDaemons..."

# Remove user launch agents
if [ -f ~/Library/LaunchAgents/com.macpaw.CleanMyMac3.Scheduler.plist ]; then
    echo "Removing CleanMyMac3 user scheduler..."
    rm ~/Library/LaunchAgents/com.macpaw.CleanMyMac3.Scheduler.plist
fi

# Remove system launch daemons
echo "Removing system launch daemons..."
sudo rm -f /Library/LaunchDaemons/com.barebones.authd.plist
sudo rm -f /Library/LaunchDaemons/com.macpaw.CleanMyMac3.Agent.plist
sudo rm -f /Library/LaunchDaemons/com.microsoft.office.licensing.helper.plist
sudo rm -f /Library/LaunchDaemons/net.telestream.LicensingHelper.plist

echo ""
echo "Step 3: Removing PrivilegedHelperTools..."

# Remove the helper tools
echo "Removing Google Drive Icon Helper..."
sudo rm -f "/Library/PrivilegedHelperTools/Google Drive Icon Helper"

echo "Removing BBEdit helper..."
sudo rm -f /Library/PrivilegedHelperTools/com.barebones.authd

echo "Removing old Microsoft Office licensing helper..."
sudo rm -f /Library/PrivilegedHelperTools/com.microsoft.office.licensing.helper

echo "Removing CleanMyMac3 Agent..."
sudo rm -f /Library/PrivilegedHelperTools/com.macpaw.CleanMyMac3.Agent

echo "Removing Telestream licensing helper..."
sudo rm -f /Library/PrivilegedHelperTools/net.telestream.LicensingHelper

echo ""
echo "Step 4: Verification..."
echo ""

# Check what's left
echo "Remaining items in /Library/PrivilegedHelperTools/:"
ls -la /Library/PrivilegedHelperTools/

echo ""
echo "Cleanup complete! The following should remain:"
echo "  - Adobe Acrobat Reader helpers"
echo "  - Docker helpers"
echo "  - CleanMyMac4 (current version)"
echo "  - Malwarebytes"
echo "  - NordVPN"
echo "  - Zoom"