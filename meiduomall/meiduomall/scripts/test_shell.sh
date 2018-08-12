!/bin/sh


mkdir demo
cd demo
for ((i=0; i<10; i++)); do
    touch demo_$i.txt
done
