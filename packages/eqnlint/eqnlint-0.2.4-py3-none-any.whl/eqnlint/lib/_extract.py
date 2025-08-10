# lib/_extract.py
import re

EQN_ENV = r"(\\begin\{equation\*?\}.*?\\end\{equation\*?\})"
EQN_DSP = r"(\\\[.*?\\\])"
EQN_INL = r"(\$(?:[^$]|\\\$)+\$)"
ALL_EQN = re.compile("|".join([EQN_ENV, EQN_DSP, EQN_INL]), re.DOTALL)

def extract_equations_with_context(tex):
    out=[]
    for m in ALL_EQN.finditer(tex):
        start,end = m.span()
        cstart = tex.rfind("\n\n", 0, start)
        cstart = 0 if cstart==-1 else cstart
        cend = tex.find("\n\n", end)
        cend = len(tex) if cend==-1 else cend
        out.append({"equation": m.group().strip(), "context": tex[cstart:cend].strip()})
    return out

def extract_citations_with_context(tex):
    pat = re.compile(r"(\\cite\{.*?\})|(\\bibitem\{.*?\})", re.DOTALL)
    out=[]
    for m in pat.finditer(tex):
        start,end = m.span()
        cstart = tex.rfind("\n\n", 0, start); cstart = 0 if cstart==-1 else cstart
        cend = tex.find("\n\n", end); cend = len(tex) if cend==-1 else cend
        out.append({"citation": m.group().strip(), "context": tex[cstart:cend].strip()})
    return out