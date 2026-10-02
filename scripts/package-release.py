#!/usr/bin/env python3
"""Create a Package Format v2 archive from clean, tagged Windows x64 Release source."""
import argparse, hashlib, json, pathlib, re, struct, subprocess, sys, zipfile

def sha(data): return hashlib.sha256(data).hexdigest()
def git(root,*args): return subprocess.check_output(['git',*args],cwd=root).decode('utf-8').strip()
def document(data,name):
 data.decode('utf-8','strict')
 if not data.strip() or b'\0' in data or len(data)>1024*1024:raise ValueError('Invalid document: '+name)
def pe(data,name):
 if data[:2]!=b'MZ' or len(data)<64:raise ValueError('Not a PE binary: '+name)
 offset=struct.unpack_from('<I',data,0x3c)[0]
 if data[offset:offset+4]!=b'PE\0\0' or struct.unpack_from('<H',data,offset+4)[0]!=0x8664:raise ValueError('Not Windows x64: '+name)
def add(z,name,data):
 info=zipfile.ZipInfo(name,(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16
 z.writestr(info,data)
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--build-dir',type=pathlib.Path,required=True)
 parser.add_argument('--output-dir',type=pathlib.Path,required=True)
 args=parser.parse_args()
 root=pathlib.Path(__file__).resolve().parent.parent
 cfg=json.loads((root/'release-config.json').read_text(encoding='utf-8'))
 if git(root,'status','--porcelain','--untracked-files=all'):raise ValueError('Source must be clean')
 commit=git(root,'rev-parse','HEAD'); tag='v'+cfg['version']
 if git(root,'rev-parse',tag+'^{commit}')!=commit:raise ValueError('Version tag must identify HEAD')
 cache=(args.build_dir/'CMakeCache.txt').read_text(encoding='utf-8')
 if 'CMAKE_BUILD_TYPE:STRING=Release' not in cache:raise ValueError('A Release build is required')
 home=re.search(r'^CMAKE_HOME_DIRECTORY:INTERNAL=(.+)$',cache,re.M)
 if not home or pathlib.Path(home[1].strip()).resolve()!=root:raise ValueError('Build must use this source checkout')
 folder=cfg['folder']; payload=args.build_dir/folder
 entries={'README.md':(root/'README.md').read_bytes()}
 document(entries['README.md'],'README.md')
 for path in sorted((root/'LICENSE').rglob('*')):
  if path.is_file() and path.suffix.lower() in {'.txt','.md'}:
   name='licenses/'+path.relative_to(root/'LICENSE').as_posix(); data=path.read_bytes(); document(data,name); entries[name]=data
 source={'id':cfg['id'],'version':cfg['version'],'tag':tag,'commit':commit,'repository':'https://github.com/pondashicom/'+cfg['id'],'source':'https://github.com/pondashicom/'+cfg['id']+'/tree/'+commit}
 entries['licenses/RELEASE-SOURCE.md']=('# Release source\n\n'+''.join(f'- {key}: {value}\n' for key,value in source.items())).encode('utf-8')
 for name in cfg['payload']:
  path=payload/name
  if path.is_symlink() or not path.is_file():raise ValueError('Missing payload: '+name)
  data=path.read_bytes()
  if path.suffix.lower() in {'.dll','.exe'}:pe(data,name)
  elif name!='VST3-SDK-LICENSE.txt':raise ValueError('Unexpected payload: '+name)
  if name=='VST3-SDK-LICENSE.txt' and data!=(root/'LICENSE/third-party/VST3-SDK-LICENSE.txt').read_bytes():raise ValueError('SDK license does not match source')
  entries['payload/'+folder+'/'+name]=data
 manifest={'formatVersion':2,'id':cfg['id'],'version':cfg['version'],'contract':cfg['contract'],'agreements':[{'path':'licenses/'+name,'sha256':sha(entries['licenses/'+name])} for name in cfg['agreements']]}
 if cfg['runtimeStatus']:manifest['runtimeStatus']=1
 entries['manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 if len({n.casefold() for n in entries})!=len(entries):raise ValueError('Duplicate package paths')
 out=args.output_dir/(cfg['id']+'-'+cfg['version']+'-windows-x64.vtrponaddon')
 if out.exists():raise ValueError('Refusing to replace existing package: '+str(out))
 out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',allowZip64=False) as z:
  for name,data in sorted(entries.items()):add(z,name,data)
 with zipfile.ZipFile(out) as z:
  if z.testzip():raise ValueError('Archive CRC failure')
 record={**source,'filename':out.name,'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'files':[{'path':name,'sha256':sha(data),'bytes':len(data)} for name,data in sorted(entries.items())]}
 (out.parent/(out.name+'.inventory.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:record[k] for k in ['id','version','commit','filename','sha256','bytes']},ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as e:sys.exit(str(e))
