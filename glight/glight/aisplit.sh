#!/bin/bash

# Define the input file and the prefix for the output files
INPUT_FILE="glight.py"
OUTPUT_PREFIX="glight_part_"
NUM_PARTS=4

# --- Step 1: Split the file into 4 parts ---
echo "Splitting '$INPUT_FILE' into $NUM_PARTS parts..."
# Using -d to get numeric suffixes (00, 01, 02, 03)
# Using -a to specify the length of the suffix (2 digits)
# Using --additional-suffix to add a custom suffix like .txt or .part
split -n $NUM_PARTS "$INPUT_FILE" "${OUTPUT_PREFIX}" -d -a 2 --additional-suffix=".part"
echo "File split complete. Parts created: ${OUTPUT_PREFIX}00.part to ${OUTPUT_PREFIX}0$(($NUM_PARTS-1)).part"
echo ""

# --- Step 2: Iterate through each part and copy to clipboard ---
for i in $(seq 0 $(($NUM_PARTS-1))); do
    # Format the part number with leading zeros (e.g., 00, 01)
    PART_NUMBER=$(printf "%02d" $i)
    PART_FILE="${OUTPUT_PREFIX}${PART_NUMBER}.part"

    if [ -f "$PART_FILE" ]; then
        echo "--- Copying '$PART_FILE' to clipboard ---"
        cat "$PART_FILE" | xclip -selection clipboard

        echo "Content of '$PART_FILE' is now in your clipboard."
        echo "Please paste it into your desired location (e.g., the chat window)."
        echo "Press Enter to copy the next part..."
        read -s # Read a single character silently (waits for Enter)
        echo ""
    else
        echo "Warning: Part file '$PART_FILE' not found. Skipping."
    fi
done

echo "All parts have been processed. You can now delete the temporary part files."
echo "To clean up: rm ${OUTPUT_PREFIX}*.part"
