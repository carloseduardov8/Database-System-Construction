from Record import *
from Block import *
from BTree import *

class Hash:
    def __init__(self, disk_name="Hash.cbd", indexBy=[], indexBTree=True):
        maxDegreeBTree = 5
        self.r_block = Block(disk_name)
        self.w_block = Block(disk_name)
        self.indexes={}
        self.indexBTree = indexBTree
        for i in indexBy:
            if indexBTree:
                self.indexes.update({i:BTree(maxDegreeBTree)})
            else:
                self.indexes.update({i:open(i+"_"+disk_name,"w+")})

    def __del__(self):
        if not self.indexBTree:
            for i in self.indexes:
                self.indexes[i].close()

    def insert(self, string):
        rec = Record(string)
        self.w_block.write(abs(hash(rec.cpf)//10**6)*self.w_block.max_size*self.w_block.record_size, rec)
        self.w_block.persist(abs(hash(rec.cpf)//10**6)*self.w_block.max_size*self.w_block.record_size)
        for i in self.indexes:
            if self.indexBTree:
                self.indexes[i].insert(getattr(rec,i))
                self.indexes[i].search(getattr(rec,i))[0].pos=abs(hash(rec.cpf)//10**6)*self.w_block.max_size*self.w_block.record_size
            else:
                self.indexes[i].write(getattr(rec,i)+" "+str(abs(hash(rec.cpf)//10**6)*self.w_block.max_size*self.w_block.record_size)+"\n")
                self.indexes[i].flush()

    def join(self,other_hash,field):
        pos=0
        self.r_block.read(pos)
        while(self.r_block.records[0]):
            for i in self.r_block.records:
                if i=='\x00'*138:
                    break
                if field=="cpf": #if field is primary key cpf
                    other_hash.r_block.read(abs(hash(Record(i).cpf)//10**6)*self.w_block.max_size*self.w_block.record_size)
                    if other_hash.r_block.records[0]!='\x00'*138:
                        print(i+"\n"+str(other_hash.r_block.records[0])+"\n")
                else:
                    if field in other_hash.indexes: #if field is indexed
                        if other_hash.indexBTree:
                            other_hash.r_block.read(self.indexes[field].search(getattr(Record(i),field))[0].pos)
                        else:
                            for line in other_hash.indexes[field]:
                                if getattr(Record(i),field)==line.split()[0]:
                                    other_hash.r_block.read(line.split()[1])
                        for j in other_hash.r_block.records:
                            if not j:
                                break
                            if getattr(Record(i),field)==getattr(Record(j),field):
                                print(i+"\n"+j+"\n")
                    else:
                        print("The requested field is not supported.")
                        return
            pos+=self.r_block.max_size*self.r_block.record_size
            self.r_block.read(pos)

#a=Hash("teste1.cbd")
#a.insert("11111111111;54.037.661-5;estermoro@gmail.com;06/01/1952;Feminino;Yuri Matheus Antonia;5942.00")
#b=Hash("teste2.cbd")
#b.insert("11111111111;54.037.661-5;estermoro@gmail.com;06/01/1952;Feminino;Yuri Matheus Antonia;5942.00")
#a.join(b)
