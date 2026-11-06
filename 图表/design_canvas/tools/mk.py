import re,sys
s=open(sys.argv[1],encoding='utf-8').read()
s=s.replace('<script src="./support.js"></script>','')
s=re.sub(r'<script type="text/x-dc".*?</script>','',s,flags=re.S)
for k,v in {'6fb6a1fbb210442fc20eb36d9d510346':'drone','d15f94499e964d7038eaa5d1f2e15735':'pointcloud','a646c67ce9be84e224eae73c3fed3463':'threeframe','f64253a3a18a5c9292a5f2bb1feb0676':'environment','aff9bc8c320638e461d94abc1100d791':'noisytraj'}.items():
    s=s.replace('/_blob/'+k,f'../assets/{v}.png')
s=s.replace("font-family: 'Tinos', 'Times New Roman', serif","font-family: 'Liberation Serif', serif")
open(sys.argv[2],'w',encoding='utf-8').write(s)
