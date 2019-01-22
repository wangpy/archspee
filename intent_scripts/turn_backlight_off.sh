#!/bin/bash
FILES=(
    '/sys/class/backlight/rpi_backlight/bl_power'
    '/sys/class/backlight/soc:backlight/bl_power'
)

for FILE in "${FILES[@]}"; do
    if [[ -e $FILE ]]; then
        sudo sh -c "echo 1 > $FILE"
    fi
done
