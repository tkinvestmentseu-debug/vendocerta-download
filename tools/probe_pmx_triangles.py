import io, os, struct, sys, json

def read_i32(f): return struct.unpack('<i', f.read(4))[0]
def read_f32(f): return struct.unpack('<f', f.read(4))[0]
def read_idx(f, n):
    f.read(n)
def read_text(f):
    n=read_i32(f)
    if n<0: raise ValueError('negative string length')
    f.read(n)

def probe(path):
    with open(path,'rb') as f:
        magic=f.read(4)
        if magic!=b'PMX ': raise ValueError(f'not PMX: {magic!r}')
        version=read_f32(f)
        hs=f.read(1)[0]
        h=list(f.read(hs))
        if len(h)<8: raise ValueError('short PMX header')
        encoding, add_uv, vix, tix, mix, bix, moix, rix = h[:8]
        for _ in range(4): read_text(f)
        vcount=read_i32(f)
        for _ in range(vcount):
            f.read(12+12+8+add_uv*16)
            wt=f.read(1)[0]
            if wt==0: f.read(bix)
            elif wt==1: f.read(bix*2+4)
            elif wt==2: f.read(bix*4+16)
            elif wt==3: f.read(bix*2+4+36)
            elif wt==4: f.read(bix*4+16)
            else: raise ValueError(f'unknown weight type {wt}')
            f.read(4)  # edge scale
        index_count=read_i32(f)
        if index_count<0 or index_count%3: raise ValueError(f'invalid face index count {index_count}')
        return {'file':os.path.basename(path),'pmx_version':version,'vertices':vcount,'triangles':index_count//3,'face_indices':index_count}

if __name__=='__main__':
    results=[]
    for p in sys.argv[1:]:
        try: results.append(probe(p))
        except Exception as e: results.append({'file':p,'error':repr(e)})
    print(json.dumps(results,ensure_ascii=False,indent=2))
