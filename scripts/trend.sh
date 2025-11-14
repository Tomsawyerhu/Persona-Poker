for file in $(ls -tr ../logs/*.txt); do
     echo "=== $file ==="
     tail -n 50 "$file" | grep -E "(Player name=|n_chips=)" | tail -6
     echo ""
   done