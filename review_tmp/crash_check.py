from pysat.card import CardEnc, EncType
for kind,lits,b in [("atleast",[1,1],3),("atleast",[],1),("atmost",[1,2],-1),("atleast",[1,2],2)]:
    try:
        c=getattr(CardEnc,kind)(lits=lits,bound=b,top_id=5,encoding=EncType.seqcounter); print(kind,lits,b,"ok",c.clauses)
    except Exception as ex: print(kind,lits,b,"EXC",type(ex).__name__,ex)
import cegar944b, cegar944
for mod in (cegar944b, cegar944):
    for spec,dmin,dmax in [("Z4",1,3),("Z5",1,4),("Z6",1,5),("Z6",9,9)]:
        try: print(mod.__name__, spec, dmin, dmax, "->", mod.run(spec,2,dmin,dmax,maxiter=50))
        except Exception as ex: print(mod.__name__, spec, dmin,dmax,"EXC",type(ex).__name__,ex)
