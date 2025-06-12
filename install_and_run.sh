echo "Installing required python packages..."

# Check if prerequisites.txt exists
if [ -f "prerequisites.txt" ]; then
    # Install system packages using apt with xargs
    xargs sudo apt install -y < prerequisites.txt
else
    echo "Error: prerequisites.txt not found!"
    exit 1
fi

echo "Installation successful! Running your pipeline"
python3 UAGS_Reduction.py