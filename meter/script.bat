call activate "D:\Anaconda3\envs\tens2.3"
python dohlyzer.py -f dump_00001_20200111222621.pcap -c ./dump_00001_20200111222621.csv
python dohlyzer.py -f dump_00002_20200111232233.pcap -c ./dump_00002_20200111232233.csv
python dohlyzer.py -f dump_00003_20200112004539.pcap -c ./dump_00003_20200112004539.csv
python dohlyzer.py -f dump_00004_20200112015042.pcap -c ./dump_00004_20200112015042.csv
python dohlyzer.py -f dump_00005_20200112025337.pcap -c ./dump_00005_20200112025337.csv
python dohlyzer.py -f dump_00006_20200112040340.pcap -c ./dump_00006_20200112040340.csv
python dohlyzer.py -f dump_00007_20200112051950.pcap -c ./dump_00007_20200112051950.csv
call conda deactivate