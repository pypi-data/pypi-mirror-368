#!/bin/bash

# Script to update remaining Vibe workflows from commands to steps format
# This converts echo-heavy workflows to guidance-oriented ones

set -e

WORKFLOWS_DIR="vibe/workflows/data"

echo "🔄 Updating remaining Vibe workflows to guidance format..."

# Function to convert a workflow from commands to steps
convert_workflow() {
    local file="$1"
    local temp_file="${file}.tmp"

    echo "Converting $file..."

    # Use sed to replace 'commands:' with 'steps:' and simplify echo statements
    sed -E '
        # Replace commands: with steps:
        s/^commands:/steps:/

        # Remove standalone echo commands that just show headers
        /^  - "echo '"'"'[🔍📚🧪💡🎯♻️🌐📁📦⚡🔄].*'"'"'$/d
        /^  - "echo '"'"'=+'"'"'$/d
        /^  - "echo '"'"''"'"'$/d

        # Convert echo statements to guidance format - remove echo wrapper
        s/^  - "echo '"'"'([^'"'"']*)'"'"'$/  - "\1"/

        # Convert complex commands with echo to guidance format
        s/^  - "echo '"'"'([^'"'"']*)"'"'"' && (.*)$/  - "\1: \`\2\`"/

        # Convert bare commands to guidance format with explanation
        s/^  - "([^"]*)"$/  - "Execute: \`\1\`"/

        # Fix double-wrapped quotes
        s/^  - ""(.*)""$/  - "\1"/

    ' "$file" > "$temp_file"

    # Only replace if the conversion was successful
    if [ -s "$temp_file" ]; then
        mv "$temp_file" "$file"
        echo "✅ Converted $file"
    else
        rm -f "$temp_file"
        echo "❌ Failed to convert $file"
    fi
}

# Find all workflows that still use commands:
echo "Finding workflows with 'commands:' format..."
remaining_workflows=$(find "$WORKFLOWS_DIR" -name "*.yaml" | xargs grep -l "commands:" | head -15)

if [ -z "$remaining_workflows" ]; then
    echo "✅ No workflows with 'commands:' format found!"
    exit 0
fi

echo "Found workflows to convert:"
echo "$remaining_workflows"
echo ""

# Convert each workflow
while IFS= read -r workflow; do
    if [ -n "$workflow" ]; then
        convert_workflow "$workflow"
    fi
done <<< "$remaining_workflows"

echo ""
echo "🎉 Batch conversion complete!"
echo ""
echo "📋 Next steps:"
echo "  - Review converted workflows manually"
echo "  - Test with: uv run vibe guide \"<workflow name>\""
echo "  - Fine-tune guidance text as needed"
