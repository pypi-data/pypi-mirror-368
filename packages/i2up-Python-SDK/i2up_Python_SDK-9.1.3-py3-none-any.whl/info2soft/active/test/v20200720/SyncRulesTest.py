
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'/Users/chengl/Desktop/sdk/python-sdk/')

import unittest
from info2soft.active.v20200720.SyncRules import SyncRules
from info2soft import Auth
from info2soft.fileWriter import write
from info2soft.compat import is_py2, is_py3

if is_py2:
    import sys
    import StringIO
    import urllib

    # reload(sys)
    sys.setdefaultencoding('utf-8')
    StringIO = StringIO.StringIO
    urlopen = urllib.urlopen
if is_py3:
    import io
    import urllib

    StringIO = io.StringIO
    urlopen = urllib.request.urlopen

username = 'admin'
pwd = 'Info1234'
    
                
class SyncRulesTestCase(unittest.TestCase):

    def testDescribeSyncRulesObjInfo(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'rule_uuid': 'c3FBc77A-aA76-A8E2-8ACe-6d763dfdA255',
            'usr': '',
            'sort': '',
            'sort_order': '',
            'search': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesObjInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesObjInfo', body)

    def testDescribeSyncRulesDML(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': '10',
            'usr': '',
            'rule_uuid': '166b9eed-CE78-1ef9-9545-09FdB6Cbe2ac',
            'sort_order': 'asc',
            'search': '',
            'sort': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesDML(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesDML', body)

    def testDescribeSyncRulesProxyStatus(self):
        a = Auth(username, pwd)
        body = {
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesProxyStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesProxyStatus', body)

    def testCreateSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': 'ctt->ctt',
            'src_db_uuid': ' 1B1153F6-DAD9-BC39-888A-A743FCC208E5',
            'tgt_db_uuid': ' D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'tgt_type': 'oracle',
            'db_user_map': {
            'CTT': 'CTT',},
            'row_map_mode': 'rowid',
            'map_type': 'user',
            'table_map': [{},],
            'dbmap_topic': '',
            'sync_mode': 1,
            'start_scn': 1,
            'full_sync_settings': {
            'keep_exist_table': 0,
            'keep_table': 0,
            'load_mode': 'direct',
            'ld_dir_opt': 0,
            'his_thread': 1,
            'try_split_part_table': 0,
            'concurrent_table': [
            'hello.world',],},
            'full_sync_obj_filter': {
            'full_sync_obj_data': [
            'PROCEDURE',
            'PACKAGE',
            'PACKAGE BODY',
            'DATABASE LINK',
            'OLD JOB',
            'JOB',
            'PRIVS',
            'CONSTRAINT',
            'JAVA RESOURCE',
            'JAVA SOURCE',],},
            'inc_sync_ddl_filter': {
            'inc_sync_ddl_data': [
            'INDEX',
            'VIEW',
            'FUNCTION',],},
            'filter_table_settings': {
            'exclude_table': [
            'hh.ww',],},
            'etl_settings': {
            'etl_table': [{
            'oprType': 'IRP',
            'table': '',
            'user': '',
            'process': 'SKIP',
            'addInfo': '',},],},
            'start_rule_now': 0,
            'storage_settings': {
            'src_max_mem': 512,
            'src_max_disk': 5000,
            'txn_max_mem': 10000,
            'tf_max_size': 100,
            'tgt_extern_table': '',},
            'error_handling': {
            'load_err_set': 'continue',
            'drp': 'ignore',
            'irp': 'irpafterdel',
            'urp': 'toirp',},
            'table_space_map': {
            'tgt_table_space': '',
            'table_mapping_way': 'ptop',
            'table_path_map': {
            'ddd': 'sss',
            'ddd1': 'sss1',},
            'table_space_name': {
            'qq': 'ss',},},
            'other_settings': {
            'keep_dyn_data': 0,
            'dyn_thread': 1,
            'dly_constraint_load': 0,
            'zip_level': 0,
            'ddl_cv': 0,
            'keep_bad_act': 0,
            'keep_usr_pwd': 1,
            'convert_urp_of_key': 0,
            'ignore_foreign_key': 0,},
            'bw_settings': {
            'bw_limit': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',},
            'biz_grp_list': [],
            'kafka_time_out': '!4Hce[pBcYtQ#]RrJcUB2iRSeC99g)3ql4kCrA(%j*NQaA^5eE$CJU^VNXujipcyjiG#JykHw$DoMg7zThxviQRx&sxmKZr4(@n8)[cSp]0$&YIOwHUWdBEnjq[*[8C$HL@wf@[!ywEluSr4IG!AgKq8XuXo(Zworua&AAE[G4j9$nf*bNrhl%XjSEUz!^TKP(6G$2bl7#ZSzq4#R^RXCSS8wit#Cu2l*Pix^ZIg#xE%Ce!&yV)QoWtgc)7kTJqM%g6gxiRP3m(XMLIx6xt0KpOk%ydFQ%5YW)%y*BE1!%NBdIStbk0])g!&xVwvy9i%O%G26f$Ik#F5(tK1%Ne0k7*M3&uJRENIh3Hw^zw#JWD%y^ens6lWRJ]LqhIE0)Vrg7iF0WWY14@lwk$2)*zp$Y(GWAkaBOA*peSStro[Os(@fkpMIy4gf3m1j4]#ti^J&pgOD@%NoXiK!tF6hqAxDu8kz29Oca1HtVuTV5y@F4^!lggz*dsIZ[5Ou(bUoE[#R1G2l7nFR(cyqRys35IKoZ)z#Qn2cG8T@9GFW4[skx1PthJGo2Rr*eyzHRosrd(PC0qHE6SwD[s&Cq4&Tj&GN&OG1vWGeqU7fxlQOBS(D%]K)MraDkwHEGDmWpK)bhfzuOaJf)p5ZsU7M@O4f!#4BHXTHtMgs%^8mqcItR!17$DTXZJuE9ZN2Scrq&qpfwB804POb%5c#6DKjd^6Tsc^cdtwH#n**B^uDQ9&zWqiXO2QyLbqZ9VdVN&a*53N)F8Zr*Q08TC@0m[CPk0Nt@*VpFN&B!w(sn^lRfX2rg94n!5heHm4VotZVI!rhU9EJZ5p7*eAdyr)NC[ZvMa9)]1*oFiWsl%z@!8qHm7&GIfL]*3EyAnHMjGCh^RT6nBuq61NCOFT)]@uJfe[lNlG)K7t6(M6&!(Wv6s6VwJXp0pTLBj3qhw4yrKfOa*k[l1Cp4@EltdxB8wonKc3cJdkd^koq5IjUkL*SzeF5ZWfJ^e&QDKG6EP2YgEuWBqviDTy(BCS[WhsG^(S0ES@DXiD3@kaGLhX4Mk7tC((MKM^7G[Wygd8FCuD%krKPLuTz*bnXwj#LSiMqarCshod)ekFl%P!BOFq^##Bc%S4PVFi^NZzi98CbDq&D7ijV&M)4TIG1M#9Mf%t9h#G9zc])8SnzqMygU)u9S2zsgnX9B8KJ^RgsZ84My*s49QjYCSxZJK9lUCfDh)!SRdSN5owBzHBMBX#5APkySV7f#XD$e!X&IY3nLBKIkb2$GwMgx]KYeN#Zp*1%EEOIb9QVB3wE8Iwr2E1VC7uTAxqci@4fDr@bKk2RwMIFGPnNp()4@l7tvf]yzGmN*Pi)GYA&F$l[GWNmpskE2(B24@smPP^@IL)4^KKneZM!edoxoXVcV5yA1w6mm#R9xTcf4f5L454BoURRiaLaT)H0bP3#KKrW@ST5^pGP79BkjV!8AZTX!lkJ8Ih6vj)0RLS)vVZspZ!fM)p&M6Mjs)7i4@yWGdF[5ju5Euq^0F[R8fb0Ckio(5%($[)P7^7x8xn&Ks!Wzq8iC8NFNsOOtTedgCewgzG^Q0%YJrh!c*mwRFc#1J39wIxi7oJ(Gy3ejW6WN0$U%oCYd(FKnOZA0PU)[zDfbzj2lMrdFeHB8R%T8G8OC9P5^h4H0Zo2*[^%n2dZx(7BIE9X(9]Xl&A7i#(Vek1wNXAMQ5Y94npDJOT%q^*1xet!Qj5j&VXVciLFbyaA7^q*l&P!p0SgF6Hx!NHFgtNb4qQ@x[Cpk3B0Ka*U7JL[Sr@m9X7oB8pI$RYKTXtKzCr&88403#5uAcv3&c6bXxaAL!7qv9dWnJy7uSqc4wPs$gGxYEOIT9(u3Cln#HZs#@&yu*A6Z6elH62&wi^IhWY^V)X!skN6A@fv7mx&%N2Ty%D0qMCEDW!8fUxyvspZHPPMhgcOZ&A&cJ6p$*YnIf8cyAsVdCwghV6KOGBlSqFXA#I4g42buN61s1CRuzmz8xzeLpCxsXxdTq0QywS4kck0yc9m^zCYX5GdgFUjE(OkvMeXD!pJ[SxQBR4wgvs@1aCMJdgY&n)m!N2BXZQ4mDreL1o4U*9o(1Oy4V$!PT[YBfc&HuCfImA(kyud(NRxlhIX3Gs7MU!b0y5YP)sjmUit7wlunj[IOdKneyUIchy!dhhRTyDxfGoZKRgxyGEyQ0WOoIzwVIYD)nNFKhv&BkHvDZ[s*LOsS3!sL)nWu*jR$ZOH2v5OezM4QvuKebFF]RK*V$oeTUSxcIUNUe&K1IJnrxVyLdfQkaNw#KxHvS6EJ]FFEpg#SL8RSyif0nzsTFlZmRT#ZX@lU$kdlEALGbs$Lo6V4Euq%gQ^AcLZJ)^R%vx)[Pv)B3%FaLZu&ylwM32F%2RA4Cjg%1O%@Qfyp8Ryd$@%s5!NOKfiy^H7m2DvkWT7d]Z4B^z$QHnw@oP8(vpUj@xVJ!pf#Jzj9!RJeXT0qK%P20P)hhv@5gDq%FOTUl)YU&Zn&wOs07LrHfLCK8u9pD)SDYn&@qwwN])43o3mI17dtQz2c$ELGKTRwzLkTQ&h%xD9hsUnep!MxxgFSuAkEnsO$(Ja!3O8RAKv2r2L63dx5IbaokhoNDNt*6DZ7C8OoWhc1m&HnV0Y3%lfvu(MF4P[^hS7NF!l9KiGQ8p7ooA@4$ny3twFV#&K])dl)3zJxh^CWdMPfrw!8quej8TdTc&#y)LYqM*o@p)JicPuLaYg1!!3Hu[gL0X#QpGXy0bHb8[1*$)sein#90noEW(PkqYWSNJfL2^Enzk#(GVAQZcqLqQP&QY4[UD8MiMGI&y8asIXZDUB$6a3NQxz^wM$z6s)1z1euNlzDRFP)DKHzkeT#WzTw1Yc1MVBd(9Fepoox%SobfLCDf08I9m3Uub@XGn(f4&)OMs)R^bcm(3hY3K4Z4OhFq)Wjnvx&f0j8Fmt2vNOAV!77xsB0dpQYKAD%uidKVYqbxl1$KRGl7n#ENsp$y!r$f3Js2FIcl7IfI68QqmV2tgH1QM)&KfmulN7YUlgTGfp[TnV$$N68]i$MID&AvcYmVuTd3vz)7HLAP5BnU9zqKOBYx*g@NRTworr&Ahe))4E[O!#1*W7ej#Gr!kfGIDRkVRXS^[XnUJ9ZmSt6!NP2NPPet^sEGtszckEyr29DYhB2qjtK$nmgZv@(cYOU@itKqqdy!qVhXMklWFqIospjRjaISbf*yW^)u438*]54HXLsmrDZr9[hmjax^Z$WVRvH!7vFPceyqE^!1AJLe4SPDw(YR7TqJUD2[$ZBuO*H0C%0dh@Ciu&T9LeQZFfs9CF^4TyBlKpoX$MyD3PRqq9*M@PS9$!Q%p2Ouzf1XVtb!O4vr%PlMZ)s!Li9Shwsz&gX3[CSykTHQAVmE2il!SrZk7%j]HyBpM6D@6Oo2ftNh#(Q*h!4[dBWsP1C7T]STfgtqHsIR5YMu1NDGeZUonH6tKBdi$ZfQCrZeDEZfAWFeN$^&Ol*pxDr#h6op@g*LGq5vw]4DL$JZ2*5#cCR*!w9pZ3su3dAwJrYm067!I#FzFCvx9@j[bYi8C2jMug@@fmYc6*pIpCC5Wco^]cjdk1PJ1e##3HDjA4rC)ZBpVhf2E[fuyErpFmTndw2g7d#UhTj3vlQEDWEVz&dKnc#6l64%JTHBgEn4NST[lnn^ll]cvJ!o*Z##%!Skxb#QuDs#Zy$H7)%BiuyZcIW)WpAs4(Fm3Y[r6QlN1aMdK18Zb6dRsy(C!GLceK(fvtleqeVEZw]tLZ*h@*%2DkH)e6IdcrX6qddOXvnqSM1!!S&zPDW^5KlJkCycHWZjepuQ$P*I[lfw%E7V9aW&pKNX9E(G5(VezY!Jf)U^Zj5]FUlJ46Vnz6$U5mMlMi#3p[ksB#Mzs5IoV5PTgzTw)^5%1Is[HyWa0AsNZVt5f@mtWr(Df1V&md4S$[(MSP9Uj)3OGuX8j^kw%tnS$&9%r*IloQZVTUsOY^L8Ra#w7Ve6StW(L64d#845IkLbuloeM2oq[34Zczoa7WUh$Sdxj^GliCG)V4cca&lsAkoO^&NB*Xc0FMg@Aw!#SUp($vmwA^K[dQA3dL5te0LE@jsM&!xZ1#vMZZ&J#61t@u$)F74@(1v2nc3EJdobEL)W%sB6]vmcy5ZQhWv(GRsh0e1cC^b6BC23tgYFR@(NBKE8N[EAA#xY!Pk6JQzS$@xTdqZn5&wsj$&DxZ$]JK4Ntpn6bRCLPtKFiPTdTiWv^^N5kqfDcq9RYuLVRE%K#F@PTzP@coAcjMkyi5*G^FAJ5Uf6jDTP@MWoNYhK[0[*ZJp7rpeU&xk3)7&RnNBBgMq(OniU63)!Q4izxxHDlEd[6K!o8MYF(VZdg7KSp(gyNMv%8gSXUrAnVcf8Q4MVHZpX)n@l[KRqm*eNR4H7EjRhhdEd8eJSj@G2[3ubTHel&chcMQMIUE1TcQ2HHcRw38l)#hli85PAobT@H$IV!9CJeO@QZZx3BxbxQMOw79)(U5Kil1bVvC8fh!qAiI*O$8jc#EIFA%fC$c4PICX](vvs@(LkQLRU#zOSQOQn5JnnHLyq[K7LlXz3a[5egr@yBgMUcT$wz*vJbjV7!VK8VV0bllVfwfIIgDR18u7UR&^!^wvUmj#xJQOUpCl#)OH(suhEuxdS2ilSK54%$tk43hnP^T859yX3Z(GdnRsTWYZrsIcuprEHSHHo2UjD1tv@rF*P2jE)4xRU2UB@6kGx([40xH$w0#JygYkFXiRk3Pw#2hSEE#X)qh[z[69dwQiCG&fp4iJYLfYJF]6GJ*kOBlGW!(qb#x9dE)]S^1m*#^zL#WE9X)&tnr5%SC7jtSVtQ6I]kcQo8dusrN(9KaJF)Tj*K6eXM&gQijBN7zpt(#Z3DQ3Ll3XBo8T%pK2O@3YuvsP*o7vM&ovtzri*SRiJSRqnElC9*CtqNxXlnR()PKbyx4RxiBsam7LCGXw&Ki8vt&0GOVDIL(4KZTHo%[Fvj2H2WcLoszUcB1CHAkxDQCuUbGE]Q%3P#$eN4t9hvK4OCOwNe*8keFfBn*X[gRKd]9rP7&kWlLNGxPnfhj8hKw3cy0Y1jlDjoc@lo@vFpF$@uCQZO&zbUHgD^Jo)Ln6C*yjgklKwk)%!)ZxGr*oj*BDSOKNEVis[&ylVH8moU^dvTBtlUG[)boQ7!Gmg)WOTbx7cjdDx%@F18BXHACJ&JTFx)NtuoV0([L5&)BFhLmT*XS]pCConhwwLjFNVefFKAuHUzPN#53#6@A^OvL$jsmzuU(HZ%#oO!tO@H03NK4kjo@FP%[js@4I&1VT4T#qnS#zKFSx$yfof&QJCkN5zU#lFLAn*yTM2EGXYRGu3FU$)nU*EjsynW&ov(4k)4TPjakxMvRiW[7Y$L@uhuw%(D[cVToT0z0V@ZU2Ox)hoQ0hoOJGBO$8x1RbP@88XKeZC]Y@&%MSYiBj@M176lHxE0v@BfHDZEj2w!$o#CK$79yEz]NP$x[6)r^D1axlPG9fnG56HZk74eaUn#cpT6DDisgmx#RTI9jQ9MZkevGbdyqwJ1zsK7TIl&E92(hl*ZCnxIBcA9$wjLtP@8ZwoIfQ&E)xv)Yqw6BGUZkJiX#N1B!iM&!WlmMe4gRMYytWQIV#TXL(SsGbW91Oq983qdDIlbfdkVGEVHlTxNOPDw$teFY3qATE4QjsxW!2gOMUhUif*xYtxoRlCEc@lGMh(^(403oYv0OqxuF%W93yTe@G[#ltr3AJUBozCE0qC2yKn2L97osp04QoXA%WAxb9htKlRtC90QgCGW8sa4Yy3N&NJXRz4&93&JCUS3z[R$ZQwDFGJVW)Ic8SIBb4JgU%33B!9OH1vumV]M$H%iZswEmnDY^x6D9N97oFO@cR1Vrw&XIXig&!G3qAPN#3en(EWKQF!*z&U3ceCGTsjL1$&Wfo]!oS6Z%vm96O9R#67ww%1uwr[ZfA!OuYnedQ3pYE$PA^e0#$QZ49*jeHCQr7w7ZPt#BJGi)EMcTK62rJz1h2TC$$ZVdJeel(YfOh%X5M*Dk*2oCz5@Bc)*u2kUbwrl!@e$$u4Tn99gT3DWISe8lkS(@Rhn8cDAHZf)MZZAN@rN0oCC5jEHhTL4UTzP%QgGtGXL7oqgkVEXmA6Db0jZKii8gOMTlhKaecmzBDwgKU#VW&dsIadm7iCg5JyHnOHiY5ULrkkAh*zeTQzsxIcvo%GjbsQmiUw4[PjTeTFgj%$qFvLT$ebhhWKI1tQ%6vitvFG&xP)niL!GA@[f2J*2*szPJTpVYOWD)i$*)m[PC7!^YOvIlpS!!85teiKHiBLyYm%V@9hhk9eQzDl5LfF^yWJWRD7hKe1TnFH)9TyNwYZZZI!XZL1bF@U@6%!IGysBO^poI@^ArzfkEyZrrro2s$1W@LrZ1YKuCr0Qz%Qjd*6B^H4R[WPsGm#k&Vo3Y)8(&56]f^FBCMU9DTfI7fbUdSMiuFl(%AtfD4NebDlzXMLlPGZdilH@^UbW^utHGBju6#[mI9l2$Xek5I5)ChPGo#WTlg%hN1Rw@tw4#U$nldhM%Y&m!EC99a2jlb%3zn4eNQ$2!s%W)%^r^w)]5DoNp9#g[TTAlSqSSVtIDKe80TGq1GuTFc4OU[u*u17aIPk*QPJkGthV@sYWzlUKKQx&aCjW7^PH%6&NuMlorCo)0*3cFP#Ej6Yn%jgH)7zV&o1eqx)7xosDJ^uDB3KRV5vzYqI5NmP5&ohxinU#x5f%^E8Hy4WFELF%b$w!DLB9Fy8f5aCLfrNUY37l$DoAEVqK2(@]tB&L&4^wYA1!pFUXK[EPYfHZxqq5pP9M0Ir*9eAj#8ur%9ejjIoJTppwg%1qRac8PTT)@44uTFLTW5u4htncfz]#Q9Za(OSVpqvm@TU!(f1t^vg5coQ88OJ)kBV^J0cJhb0CMVWUP0%t!xI4!ABAg8Kp@xVZ[boj%$[OUkIfcBb#ro$DqI$Qwv%O[]lr3k!wCkaGqh1AHMA)WPr6grHwlQild$wSS$@BW#1(Gx8!tT29$W*Ky&W$#)@G[#2*d9Lx)M3]GGz[R%blslFoftDbSNfB*Q^1eGX#$eP5dS[d*qpXr4PZXRvt%*WZ270pYB^M2cUCUouH5d6xKDDUywY4grHZJxk4T%9NX8h1LSfKgzNLVTSTtPu1[7w9Qsf$zRMYBK&KMQk@Q]AR%W4*1h)LP9N79HI7Z!x[l*8Ghl@@b)0g*$vys3Nn#TRsWBE2UtR9lnYumJl!mfM4BBiylxCwGGQzoKAcPId[*nVrsgx!uZo8i2)UufS$(sJn4NKU^$Pd$H@LD3@ayJgD18v7yRuYZSDHulFJ]n5$0hFAQsIeZu*na1oQlS&)MOtnUef5c5%95Uwi6RUiRhCP)N@4@]*tW)3*PI@rOLZCszws6%gbJd32Pb*#(sMh1!HKGhpT1blIKrELqIKw8wg[moTJ[X8CPBb5!)%J8s(l)UpRoV]*2XS5isDInCAOc(F#49rn7%)N@c$P(V4TXbCN46QUesbToAnrqgIlUojwyQpRpYvBuQz9jQkS4EznxfZc*Bx)265IUL*xJ1A$LOkImlKbZ[*D5duF1yOYlQVnDSoU7)XZU7M!@BPGX8$^r7tPnk7cJl$8Q(#JwY[GZz(ffhTp3fTe)kFJLkPt5V*(u#fpz76@$4CT9p[H[43e^z!52PT8hs)EBYyP@qjSY*dJO[4hpHjBX#KVdsHj1BxV3@4e22wT*65US^1$&9ptL(T!dgTMe@KtFeNO]eHqK86Wl0fuH[SM7KZ1mg8xA$GJ$!qV*lfA86TqE9%@d7T4$YnM7qN^W6cVZap$QWGT2607W7df[Vr5cInzygG8W4kQT@eLlX8ydZvn7CNVu9!47*eqc$$jy*OVp&D1t&S2rT#vRkGShrNS)2B9VL3vK@N]q7HfJ[vH5CpLbGqtXSmYjbF[7n1SUzoI9R$2RWs5Ce5ARK9PP3$5&u3QBBg8DMRoT8*KBzj2cLieS3AH(8H[PiS%UfqMmSiCzsz]G0aq06z)#FgL*td$l)STdNUYSuNs5UZ1gFbUErQtgfVGesYnfnJ&3znAHbAws[udje5ol(GkED!7Af9Ql$^It*WO%B^UjZ(gwsXPP!0s4k20fkwaQDm$8qvR56jYsu%gcNB@8sLVpOn2NR%KeQU2Sw)M%bSYWnyq9V09HXk^D0[8M1aji5kJB2BtM*IIAvF8b0DSFV0oGx[(^4%mqJmV2$3xjJFhKcv@zFURy[ieRSK%Y#wbkM)v*JukE[2uwIo!pPbNe02grtWXCJ@QN@pM[!@$PP2f[tL[ZYsAGSzHH]JKsHI8$[2gTb6j*DSQjQhNpLnMnh6zyiXinZQPsg4iZwI)d^gE4%uZBpMUbzo2c[ZOzJKWJmL9kp$T&Zdp&4gf)fdbh%9r!q7t6R46UW7l3%Me^m#Ycz8K^lxRg@8Nv#[9m#qj*FvP8(Tz7QIUrU8@k3qW3x[[#[c6EmvEh@h7sOhs%$@]XF0U1xyvw%boqvFT3SIvwz)KUp2USjGnDW%iBSspMNh(]PCByE3)3j*ylRNkcU9Y[MEmMO]NS[[he^M3ENFz[0[H[SEdN&4E*qFwxkRQ$V[0G)@g8JK(AR@20wH#N[7o#K0e1GFwhiZi[D@Cwox)WxSgkp$UbM(L]UVZ6gbGX^K2rk3qDt$gjT3hDE@fJD%^6UtgBd6E#gm!(NR&&D$jDHmjk2NytaRCaLfToKmdXxFs23@bF)9iLi$PkkNm7A^^L5[^MhA#Xw6*0(Vwp@@RRM3x6FU$lGmAmzJSEBWq(BFhY#VKqV]DxH^vQs0oLTXyB1ecG3JdIJdX*WMYRAIJsy6arMp8qp^C&rObl(M]%!d]Z[IcBIo7PZLSNJ1%*zimbu[PUzcZ)Bwm97#ul3*f52[hHmowAROb@UHT9bL23I7x6k#K0D(IL601Kn9$x5JUk#YtL80z7OD3W&cv8#CDZ2)&n[*hmAeAsZt@X$%&Or$PHGX[8XF3LW^xNdJdRQp$4ABE3kTe)S0HrkRqfnuQEkm1uDswFxH&7v7CIsVxIzRufmBdZLKk1We5!#6DRIj7D&SQinV^3tv)^AeM4^rLt)%6OYhm$C)8kQRSsT@g2rS17j#D[gWru!oa4p%fzcW69yPkB@p^[EZzFcirb1aZ50Q2fR$m9rTI9UJpv)IDR3pyQkrVgeAA6E$Pq#Ob]06$p)rDbf@TIlGRggM1fBQGf2wM5Q)my&fidg%JjQbgSXE4(Zl)rIMqXc#A2lYtYhAGGrA^1t$B46D2&OGk0vnG2%Hhtwv&JYUT8DcOudGVaBvy&d[o9cvJkEz!nJU*5^YS!P$kON0D1MPWvudv&L3d#u@[@S0DYtRQ]v]LPN7YqvRAdZzzKO5h9n2QUXDCr2T7jnzbq*wDPC9RsD2bK$LnWjZ@v7rqh$*INbYa]FqHXFx$IAzme^!W*Iy#*8e*rjcgVC)KpliizHm(PNENyUR0L%SKYJCXFmcllBH#IfJ&sTpbosBP7d1LDVgB#Kn*PCpQ2g9DghxICdPO2[B#KApYgw4dpQs5@SjFSM86KrsP0OOons6#RWGJ3gQX8N22ACzI5s8tv9PDO)EofRZxq8QM7F1CqTxL[X[^L6qE*ylrnZD(7S5zMQz5u5jUOz0*HBxVzddFsNKGQI80]84Cu23U1QpPEJuJfHQ2vl3uw&ojhbsK1Dy$*pVjn@W3z3a(dhF#wzg7vSdt6OHWyqnCUa1y(3f8^pf(K@uV6iunv(Jcxr!gAOcF[&sIBy6XnSu%jtHLvvFNt)Xumdz8B*[O$MdoNcekSBJhsdNO8KX*2G6IpfzgB*jEskSnavIeT*cHee^VMB0&MLxPnuBn[a(zf4xS^Y2hl)h[QfEJSuKZuWdPuWIr)N$ab7irhngnStp%AiIR2(lTO@L038xMqX5J70S5(mrWgmN79n0lPqsjQib51^S%6k3$%*&s[1hr(5KYi@PbWnFWtvIANR[Cknqf^M2U%j22ZDruD5JyCxLvR]5)hmPzLKf(B]xG!9JPHl8n[F8ZIU^ajy&I7E$!2sP9cr8VFVdSmBr7UHmhlaOWJ@FdX)C^ff18EN%RqWo7Lvv1tNHSpwRxkx4w(G0KXm^5uWK9Q%dLNJzY8lABc[fD1t67G6ziW^&2h5ZXPN3g#LnI4(KDgNx^XK#A!S(zQPw2SbXlSnnSd*H3@@(pqEC4g))gg$o9NjcBx*uYEBG1qJ!y1PeI5dPAqQNIt1a*]m!)9vL2GyvpjPAPIH$uRwrV*M5fs1#jHXos$GhOCrHnvCirpLj9*opbjUx)y*WNsFv3AYnhOCsc4@bwnMm6ysI1Y9)X(Hh!^c$zp^zu35p0YvpP^CN$]OZhO(tdtvD0^5II)I$dtmFDIIc^$[2hY)[2N8V8O%g@kh6ZoKuqSB1&YjGnwxO8f(b@u%HnX83se!WKme6zON6!7cT%qlxS@oq^zpju4KK2eS$kiSuZlZ5lvdlt@cvujl1$*XfLxu]oQhpTvw]!0ZLAx95Xx#uw&(MeF([iyh*&q$UDL5J7bSu(B*%8S2yMu(rSV%CgUWPnY]n(^XSHbxqeD!vWdk(wMqh1YR4g0MxlbG[ULF36NCJX03*Rkr7#$PzGWt17lk4b*BW*Z%XQ@PyOoMwzLUiCCLjzjS*kH1Mb0ZX4jJ%4cM)4qHlw72sGq#bQ3dM558#rjSo5i15S9Rmzsc)Q04WlE4xQixImvF85Sh5Z(H4*S8%6T%fLHX9O)cGaZs9o[xs3PDDTf6r!TWU@cGDK0]fm!mq%syhGN$wfd#r]1fWg4Ky&O[7Gz1434zME%xl1tiC0xsKI82p8$RY0gXsceMGQmNKz0NubNwpo7jF7(nxxpSUWm7OVGuCwYxRGz!drw@E6h([Q58SxvzTK%CJR3HZS&Eo4M9moLf1KOzqDL(lNkT&LEiZ!QzAaO8oY#[qupD6bo78Q8TvxB%s[n49VompW^FC66rS$NdkAHvp!kG*U(725qlx$PReQPOJPJpljdxfvvDcIl44F#42Uwb#dIvfk2Fr4&J^s1mkTsif6bvUZ6OU)kr2!rQxgOX1Mn6K0xp6#ctR4sq@B3IC4WkBotwm4@I71pBOS1KtZV4YSm[7izV#3qQh(pOjhRBLF$z70dYAyO!5Y1B($Cx0Lw24&k2fpz[OHj6iAdaDhEK%[GS]doNa4jNGIw*!ujHHpY7*w@gmgTQEBaDk0Qvi6UdAAwhNW)iS2[r$*Tjj%(xrqK6xHtP0SSys9#7@9@1ao)twY%@2b3yPN8k)@*iI6zfPbC9Li6PFC!Eq$x@XI%mMPKimP[W%itxJG&2pBXJ*J$@0r1Uqb5qt[1OyoXA54#3hEGHjgo7ZwEw5a@r#IdnBAB^c3e)Pww*dMfCgR9P&)x4o2yLwRcYv4&*QS%BCi9Bb81bZoC]*KTy%8nF0l(7PK[%pqDdnelbrsGbz]sy6A)1cKC5ocCuwu4l04M!])FwG!R1&!rsl68^AxH#dcw0q4@bI([z[AodfmW34*[h*U*2wvQ6Zoxp3HEeNGI*X!&WKfjqJnVw^qHWd9Uj0dJIVeG&FL!z0ktSd&lB6wBnY#znNHP3()rg!FusT9On!@5W22Y7a#9sGOC@Ff$D^DhIQ3J9HaFGIVgYVMFWkIWV2*Ik[c*zWLAe#kRuqnDTMA#0mz^$)DHceZ)Tqv38)Z0GYoi%#*Pt*oYZ9nDo3LMEsxN4BEiacf98yZ)7]ycQkY8$vvkqHeGW[cO3&A7PyP)qsM68gpv%*4$zvHl^C*9y$IQ2CjJXg3&QsP$hR4NFdLSry*@@D#ekKsgf@%0ETmN]ANp#(CY51HIicVa[pS*T7eCJV[yzj(abhKAhcZ5247LG97O&ttU[H7bINESM4hFx7IyjnMsofpHP6oRl%FTPM[X)mXNUno6qKccI)rjqv8mhUMk31IjKEWmTn(u$5oA*bPnO@FxZCd3JVhINS2cxTAun%$Xj9lHYLAiWL7$xCZs)P[dYTK0%t$LkT32colMQUzb5XjI[![ipAjXtPtZL4%pYJhsnS@e@#Re1^E[DXYoD(6',
            'part_load_balance': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.createSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'createSyncRules', body)

    def testModifySyncRules(self):
        a = Auth(username, pwd)
        body = {
            'row_map_mode': 'rowid',
            'map_type': 'user',
            'table_map': [{},],
            'dbmap_topic': '',
            'sync_mode': 1,
            'start_scn': 1,
            'full_sync_settings': {
            'keep_exist_table': 0,
            'keep_table': 0,
            'load_mode': 'direct',
            'ld_dir_opt': 0,
            'his_thread': 1,
            'try_split_part_table': 0,
            'concurrent_table': [
            'hello.world',],},
            'full_sync_obj_filter': {
            'full_sync_obj_data': [
            'PROCEDURE',
            'PACKAGE',
            'PACKAGE BODY',
            'DATABASE LINK',
            'OLD JOB',
            'JOB',
            'PRIVS',
            'CONSTRAINT',
            'JAVA RESOURCE',
            'JAVA SOURCE',],},
            'inc_sync_ddl_filter': {
            'inc_sync_ddl_data': [
            'INDEX',
            'VIEW',
            'FUNCTION',],},
            'filter_table_settings': {
            'exclude_table': [
            'hh.ww',],},
            'etl_settings': {
            'etl_table': [{
            'oprType': 'IRP',
            'table': '',
            'user': '',
            'process': 'SKIP',
            'addInfo': '',},],},
            'start_rule_now': 0,
            'storage_settings': {
            'src_max_mem': 512,
            'src_max_disk': 5000,
            'txn_max_mem': 10000,
            'tf_max_size': 100,
            'tgt_extern_table': '',},
            'error_handling': {
            'load_err_set': 'continue',
            'drp': 'ignore',
            'irp': 'irpafterdel',
            'urp': 'toirp',},
            'table_space_map': {
            'tgt_table_space': '',
            'table_mapping_way': 'ptop',
            'table_path_map': {
            'ddd': 'sss',
            'ddd1': 'sss1',},
            'table_space_name': {
            'qq': 'ss',},},
            'other_settings': {
            'keep_dyn_data': 0,
            'dyn_thread': 1,
            'dly_constraint_load': 0,
            'zip_level': 0,
            'ddl_cv': 0,
            'keep_bad_act': 0,
            'keep_usr_pwd': 1,
            'convert_urp_of_key': 0,
            'ignore_foreign_key': 0,},
            'bw_settings': {
            'bw_limit': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',},
            'biz_grp_list': [],
            'part_load_balance': '',
            'kafka_time_out': '&kwZYr)nOZvE&(4d!AseJMb2JRcseOpII8Pki(oINfx[EZX0oj(1siOBaTWRHcoHLrKIZ*eODNWdZw#LPI9Ehihq^7zqFrmQt0V3xdlMScyCfcO$A19bOmm^gASLb@to7X$q3$&B%5fq*3V0UQ&oy!qlHAP!d&!55Ngqcj*G]kcs2eHINE$ZKZ@xIi%5gcS^ZIqFuRdILYbj7p4idp%liWM6(GR00Dmb*RDIQKDxc1QqqGvwND(M!!!gI]86phGzP1Uf(KnQo6sMiAw%AAIsHw)VmmdpGF)wpG9EiM3I&87xArFFD25#6^WZh9$)@ZIE#a)giqeNosd#&t4$hQnLXsrIeOZBzX@@qfFmZjW2pW[2Jn$^WeZm9C^BFOfnu@uCJBqFsdQl@l8OLQMhDWhvH@fF!@LUQcf^tXtE[9)1KkiyUc]QcIrg]dhYbRUpiE(Iz6k^RvB16omhkqI@HyF]0G!)b4OB0&BgjM9ylugSf1dKyI)8XjbK977S42uzFJm0vZ%ENE&FuP9X1)gX0Lv*WqlZHY@Pp!Y(D4@QVC3hhNo[x9yczxQ2#K5UjJQECQW#[AQIe@%AKPm&WE6(NQzgD4V0c0TQW&*IOA)q%KUD0Tb5gqLjFo9T3wWVf0YGKZGarZpU)&KEe^]8*Qs%&E]X2)Nsgh#!3elEUJ17&UL*aN^g#bK9^neH&NXy[dwc$kGs(PyGnb&5vxHJ8)3hV3CKq(LLxNYUugIlyN7qSl9jPZEqSYTUS*dHTGgGokd)6wIGR$@u5r*J2SiYWB)hePQ!8O)M4MpsGKGzwy%EfEj49^549^E[8BiY(TaJc1ooYybuOhwmgeN&kRzO0nhnBD^((%WlQkwWA4CG[A*0zE2K3$lE)a3l$jFmjb1lmxiAPYusIxP!4G(DaG#dtNWtOT!@WP$Y0EkeI068TH^l$PtSd*5r2d9nyvs4rr$AtCIFPmW)6heN*%TqDpLfYELNqc44yr^1R)K!kwfAR#EN@EUZjULzVhTZjvT$iICoET&5(dH8Klxx0fY$9tA)g*5hRJ)t&OhJG#a^ATq2w!NnwM)xfzRASppKF)p9tMFOvOmj^Y9U!u@dUP5033NTLCJbuuFVcDoIxiCh1WkR%e^YO)Y)XJDul!wdpRGXaA7MPy3Z[kpW8W90!Gou&C@1%G4Yojh^4nvpICP^H@AdbdQUFFhoD4[FQih(!MV8umgs(dY5yf8yDt^lS)kb0XMdBVG&ZyrPt29eSf&pXT*(oHi37Hz5XoqY@SAs6u4JouWBGKvmm0wHLrM%05Gl@%X9%X1Y2CsXuzQ]fddurCSnJcqb#)HJbqawrvdr2XgOXjBXw8ikb$LC]8&&GSGao#SNnZfx0y2iL0mZyDVqBGGT*KjvblAfIyu^NI@$BZYi31vJUMBS]X0rp(W1AwahP^1ovmcyCwJhaH%[pNTlDN@TGGUO$UKjVENxSN6NP4iDIy$$ckPQ2egPLTE$HlkGsD$3JwSSSYpdyw$tZD6FZL)gyN29UdY@(3De(^c[hF9Wwi8skSop%c[FIcDK$NEn9L^v3p6xR($AQzMU2FQe8A19TCDy1Vqb0tc^DzgcAJv#gQ]1CNmsm2Pwd3B[ZxCX8wiaqvAqc&5GldMZ!KIFX941U7c8%92tv25ov3HEY@u2#1]qHvGvNz0pN2!FX5WVI^[B)96RBprB^l]]%Ej%O9SPoxN@[hrX(DUbRXYA$**zd8t3sMmt4C(iC%yru1gz!^eW!qs!L*TCTzTyOx5cUr9p0o8c*D8MN#d[^6rY7Pp9Rz8)OgJo^t8446%^Ycf9*un(l[[6mUK%sRmQRzFRM5@mTPK)ZDyGiYQUQ&g3SQ)AY%hInqSIplGjdeQL7$sK[9vGECegAprCksB0nP])&)dGySBnyR@Qg3C*pEY1XqOuZwRZolc@)&dWMl@Ieqvk9Nnz[e^p6lV$rZR&&djjWgbtJ&N#!FMtY5W4b[s[%6T2vt9x5r&6jAc1^(zSJxtseTHN@fNvfJfe7eKDbUDl&%dBh]OaaKoL1)v7DXk(qGxtC[@Xns2F9^teAV$CHSuUV9UoV2p&XUPX5BTC%qu3Z7vWq4dWj1)IPTCZ7mZS89!UEPF)yzP%*YeLCu76KO%QOq4a53W7k3#g(VguSR^@(EO8Ga@fi!JPEi2JU5o7F%y@Vm94GOWK6h&YxsJ4Xum@XTY1z43LVQNLzeYHAcG0TF8]iiC2(Ep^cZyqF14bRI7LM&WQbiDFYH12ix2dm0LpaYirPFX3W&kA&!vGL6GZF@NxOx#g]3YEzS7Kezhybs31Nn*J$5kHQu5&8**#GAyG4MG[EDhLDYgOW)^7CMgDbCEl)sTA%b@fwYn&tf7tS5RNk57c2py#4xvm%3ufWf5yV*aTGGVAo$uPnxt4[s57&*LSiSE@tUm^OsK2bP6[Q02&%aEwezWx*2tUUFfUW6$iRaifowYGWL$24l[$Hv*vU*HD6UtALr56d!R0i[yz#uy5DH71RTi*1Y(7KT#7K2zPb#q[PdWvJ#16WhOlgmJIy(ILOY6ofI3CdftI7ugQb&UaR#6HN2*ucyK!IeKAqfMaLc!D9OnnjRim$4!4%bD(fe&7X5FyL%WANc(zzlatYf4MYYiUT[!1M&uVo2Cr6SYwqJbw8gyr#A5)MP1ZtR)(AC*@zBcL)[hBGc#sisU1aT&&iAW6AlOjq$uhR)^YV9%vRKQdg3Wb3^H(qs@8J0@pHM[NL6mPVhuLri92Nm5SfQAtR&clP8XG3B)CRS65Lf$hI%ozBJf[1[g5@tL91tow[e3@@BY#I@e*GbUmGu[sIM[hv%RB$UfYGSKF3U3!O^g0Dqb&q&!h0C0VwaUzX&g)9rI28m(l#^9t(R2Lq#hXSZ2I%c$WhZPKnekKpo!7shMoUums!UMAaY5lHeUShXq6*@s7DpY9i%%20mrk7Dp4C[sVpnMM3u]Kq%Ejc^@^2fYQdlX#rId@xiq!W4RkzOI1V^G9@Jzr*m1J!#RM0UMCLRPOL)5tV2!Nx)iM5T4f7W%Ft^CnRvy#Z1*@yODTR#oZY@VLAYQ6F2)Xx6&O*$14OHH#!Xq&[rf8tXWLaLSH#ZxWVtFRXgk$EW0ky$XbUVx&sez%7chJlLHz!I8(4U1LgUbcD03*#e4S@LVp^oU98RElej(n6%hVFaWuT@TD9q@0jCGn5^t]TX[GLwcqRGQM^^4$V5W$H(lYVR[CCbTWliMhZKv0)fQXrlZdeKCQzR*UIACF30XW6rP2[ArNvlET*14Gz*oYrVnjTeZZp)6Fpi7CDzQH^GAWMI[iY7UBAbsKiBBb02Msc5D(pwbdLgPKq%ixRzAwbpj8ddTHuj5lVzM$s)d0DEAB@86[wpjh039MpXPUac78zFr4AU]s(&1&Wd^hj9&p6pF))dD*tEUmqJmgNRtO&tIEgdpaeXNLbKIjC1Ci!rvsK[^XvTZuA4TOQyEdIfU7Q7fiCVGm&*1FqOg(c1]2lgFBNhZB5Oi$QWKpZ^n#FE%OiYH3CzSHtTqGZ1g9iR[1c@Nd@zDijYSUBGNjrPJCT$8&xdiUqd(NuE^zNqmKRWSD5eXt*vq*yjx1KbrT1&3HA&(hD2clN!NK!7TpX@jCyN#m[DzQ9A6ln9AE&[N2uH3Gf2W(r$^1Lc34!aYoYLCNDf$A)Zvv23x74OHQdlEOG3EscuVqtmBc2oC2^%Bp13BSsHkG71LJi$zTtn[$lPDD(DM%j6CUf^0zVDkODl7lyGkA*JOQA)SvqEgW!mWTVwf&sy@E2PAUnsE2iHqoU*dsGIIi#Eyk%yk(ubiWHHL99K1xNgIx6(2*D38Uv]EhrizHw[P$*b]K[LUw1MgPqNC^@]@qCl(xdchTj*)[4Qlr$q)PsF($@C$PU!6eN%y(HeA$e8ocZe9Subg!CLF9yquFjGDg2#&kAQK)bGq$WKL6rPp(CW))nAmyZElmp]dkxPb8vrusC![P8AjvGzH7!eKA4r@UH5Qmjm0C#)ezr%r8ckv0Ql0xMRVPF1KEq]rr7R7hDDJHIC^)t5wmFZs5oK35QIMWjZXx)5ZNNI4LwE5KeM)e1W3&&bDw4rEOx40X]zd1oQsQ5EhY6YPD13*nQPx$!4lovD8#I(DBpX]FOs#lU7CVrVouDW@Ul9bPNfIT)5(x)Ecek$tn$^sWtfBQfzuv$W3kZ*y1LCyBHXo(gKDirRyHVc@HEOrDxU6CfTXY*d!NIAPJpBN5GUg5wLJ0Amlu@WFZSy&OopB%7otxU[d!G9c11el5KdnTIhcVxqp@cx*FkECS3F7rJ(r!v5XWMI4K(#^7[E#C&ewW5LP&JA4eYJw!*wX!7Rld%4fJn4&u)@*vaDm0dzuq0GjUGwNFtMUnoAY]5yF*An9W37Cm)33UxXbe03iyVoKcvFk93o!75NeA)1OyQFEo%GmVvr!vi2!)0nTYyrH1xLF%E!82A$^BqtgZueo[[2trJlfa#5ljy#6ZWnYwLXqpbF7g&9wCqZezgPUY9SBS*UF]sdm5kwHVqO1(t6DvwjU&$%qUdT8sW5Mbd#iXBEv06uoE3Pzm[x2Js9w[doM)CKtLSzuuDKUB4NqnidIhLIy&f&[[taX7yeYpcB6y[j9sbe^s9ggvY5%048KaatYFZSF&SHB)3OBId9NUFx*VhXZTFiz6DI@SDfJ$X#nwdl^20kaPhM7Ew8pTrkUIYROZ0Wu#VlJiejk#@C$IRiFDXTLX5i[1YnW8DEU%H6o(%FIzmH^er0Q0xzmArTFHaT04fVJJXwn34@h!2SMC0%g[E%E43@5V0ZP#KgJKE@KUk9!$S79kp^A3gt6TO2WvwBdIlys8oeBlmIg[N^u)!W9PSISi5f[nYvzbyrRUcEVSIIsvj4C9jb6hLZ9YKaq%viFMX(Wiy#vS9I%%$1j^sQf#&9ble%%HtEGpb#u[(jTVxBhqfeC@^fM@EILbD5%ofcgCRdrTZN@@3Z]hon%^YtTg]VFFoMuIzGXWuH39YnY5C406s2gfs61&sTyQRGQs(PDMnNEP4J*o]9YF$[#dveTEyhri$w9w6iZ*Hw3QGHWk^R6v2Fso*w50lTTk]db0R]rqVYSNW5t8RT4[W%9C5xhHlU!ag&rRGUU6QEp%oJLw$(wy^[ruvuYMwyGwXi)jXHGXE0lM[tpf@Z%Ok@d8DYstxs&uYe[Z(Gn@X9IP(Tt9XuMJ*yH!Nzo6^f5Rf!A3i35Ho%j6#DeChohVQFHuYmCccB@x)KVIMG![Nji#OlWzsHsXNxL1mAj$VC4qf)7keFE^my6sFOG$YEscypE(dQFDm!LYcX)hhUkdZX#H7NLircVj[gy^DdQjqktmG4#IsQ*ubAOCXBm9tSe7#Qo^#*QHF%Jzx^jC0601DgBF!98dfStfAl8lq(*a3mCxchQWoeqZycv9XqKr7ZbWAM^@EgMl^fludVCZcgO@zHGe1oqfInchEv&#(2*fhbQi9GP5I^cAZ&X2Wpe^spFj%wo%0w$T6*GdT8BfWVpMJgtB%6LO0CO!tv7gVYmTWl$4gEiU3[&)#CMBvp@M%of3g9ETQMrjrVb6dAA*1Mj6mI(Fu!zYRyQx1eWaVkK4QXqrYz(b7522w8n38j6$H#EWtTrFwdEsL0MvTvZWi6jOrUnlk5PqUJUN*BKp^@X1cX^BzWZNAOjAZMLAHF(X@unLy3gp$rt0t3zkcMuELi#d%DHLoORiXbU1WC![9thMnHzB70niyX@YdlCMOo!7BdFUEujy%1skX7i(#WNtvrmu[UiB35KRL2F5WHqj&FWfrqZiV45tDjaG0sltT0XlY&OoAfZQ2ZqWKmcOJQhljo89t()9pznmsy$&z5kQ&l1Nk!S3289Q)X]t(VB6^f@qm#r&CJ!myJ$nFYffyB5BsqbchJjGI5YeBZIRmSh@lVwI8vOmwN505IkWDi8w[57qyhnpUkHkAn$AV%yp7)SEXpSGDAfxTCQ6zj$Qe7ASWipIUzV%[Chy0mI3lRlK4K@mv4nrpcrNv8p4jsYX3YhXrxL5YH&#h*@J^3TQ%o!5OQgt%8E[rSCZz9Kl*hT%BwYg0cg8UU9CL7*YkzpJnAkXz1mmD0W^EKywFIoSTlGsn0Oi[Om$JL%eP%Wdtpz3qn[ehY9mV^Mzpn9XSSrciDcoZPI&qxE6KiUs&3[wTC9$!cIF07yc4tHpoL%30FmypGXAw^s&KClp@@^59BoLYE&2IGA9iZyTb*TwZMGf1gbKGr2QSPS6@MAbmf@1CnHTelF^vvWM(ALpwp#@#)JGG1&YDW#upHQ6DBMDR$SCYkAv)kbC4ET[3JGnrTwCnC&mNZ@E4*VPJGHj5FWhq86wBJP$K^D2XOrYj8@hbfJx)8kOY0zn@Bbtvic57661pn*0ou^jqrMyO0ZL!59iImOHtgYcqe%Csht!iuTzBLqM$07^avG[wV61ZKsC@MP8ZzsOT68K^7k7vv4a%yg8p8t6$nN3LW0mnZ#Z2[3hP*SPJqcY0Jmn1v)cRLkIyJjDTl(NOTQ4JrY%c$dJ(ezvMx8eR%!9N9@hOecViwmjZSx87NWiQk)b67U]gUi#IQP^FuqlKn$p[6Z3g4tYYYp$(#SuevzwLpAqBqD(h@WDReT@#Fl6P24VxlGwT*JGe[pnTp(!jgjo5TCASdB3rzLxCIV95dMDVy(@AdqYezCOfk^O2JnWKh2lLZcc5Ft05H!fHb^l7oTJ*u4GdHoTgdmJIr(A*2d&YSwiF5ynke%RGrNlR&Ht2f6LZcOO!1UCiS&2Q#Nr7NmkRf9*DEEZRDSWdn2XAKNW6pMwh9g#yMYv(4ox5PJkAqCP16V36YR#Q1G&T4n5pRQY&&TyfnrUg6Q%%4S0&C9@Gv$QRnWZP9A[Id@sMYFxDb([*ZBO^qStmIR7Euno07NmtPPGBugj(4$4i2IRdv6!I3Dn163rd&2)qSAfILN88bP11V15N3tu!(soS)vDxg)XpFS^XfFHn$xAVq$(oCG1q[IPtG[awl8JX*6fbg0nh&kti$jZ5z%G%UZRfMv45H^8oMzZf@5COMH(j!reH*@vXj!JDI%%#iub9M7^oks*uvuiEWL0(PMez0mN69nu7w(ch9$INH(GEg$3U*LZe1P*S^YifFWTyMyNs6Oiu5RU38clD9hbOu94#YdR]aroIrntl$JNfBMZ8fRRg$J[4ERL56c8uOpId$J[KP2iAM2Np6xVgjB7Evo*X*Y^ZX1(xrOn&mx)a9jQ%l^R6kdF6ocqzzW3hH!3COz^G2ORBg%id$ocUtFcp$OxzMDxjyN6v14W1WYVTAdqyecKM[s32hSClVBTu6y)$VBqWEq[)tn&7V*Z1yhTlPWVjSF(@&xd2f[LU5iyruz2Qx)6uwu0CsNxp6&$[PPlJ&heYSA$!BzPs7cO)2G6D3Pk)5ZqD$Y9dz*y(YE%T9KV&rJ@*lp20L0O1f5O468fDbbrhGOuF@e5TS#[NikVKjqGc@@zKgaMqQgvP3G#$ka@hy[J5Rl(&1n7r6s2RmvRjy036I%UkK0SC$C!Gp[*q5TLA3iBofp@0BJrE0Rio)^r4K26buPNz20w(ef#(KNDZ95@*IMe!68WXizH4yMu@FYjDdzdEb6isWtFycgHOlA*uh0RcB*c&Dn1#80q8RofYWXD06!bV9(N#wYqJdydYHv4Z)xqZkgrZPj!UgpCssX#yRANKP%a)JwLlotc!X6py^spAfYf8o9N](Cb5!*Jw2mmRoOnGqc*b5(I1TkdrWIxKb&guu5zZ5V&%C^qYj8QL!s5Tgs)KniH6hChA$h)]gpjbxYPXOgK(Wdk!xVyIK$IFSSOP!2b2MZRGa#6X#IDJE$4MQ@qBlN)QF)TcnR7uWL![yut*SJVp#n%sKFalkOADVdFnsfQs2&uU*UUPoZSPNaMnlvJM]bkje)yv!lfN^VI2mzGexax[lRIwnkoAtK*6K^B$A3pt4L%1GpC#p3fj8hRIvR43H^NV1YTZEA*HJ0MV)]VSg1HBt)Y2trd[h)2tXuNK@ciqrNLPwm47jR#pCc#UwmmMrS7*K&(Ee%I)!8egK3GsKuVq5z^Veoxa@nq8Hd!aULTXI4wnVUUNm[7ZNm)qCD(F#q0fApnU8wufM8WuNkfgfu0WP[nfWuISRX0fRQxX)zfK#qNg9F!FOB4^w(2mAt1Wf6!dWlUs6lNkwIehT)qt^VwmkgP3vku6CWDiTjQA@0Jg4tdDBI07muVB(1p(y4tN7%Ym&NW^pyUWHC&)@FPOhZBJ3j(kiH#qYGSv#ihTHmMBvw@45s]jQzyP0He&3hHE3lvti%^AU&5s#Y*aSJ#T[8trpu%*x3ZmOSbX2GUOAKiTPVxqij%Y@mJFq[MBSKFPPZHJBrd*NDcj4D&[Qb[5ktrwlDS[UE@Se1El#0WNFH^LdgOi*V)j[SsfG8yLBYJ22Q25[)5b$2p3Z6)Vg2ex15byv3)TC7%UnsVlVOWC[%zblMmbz(*O[Nd%QS#o6Hv9toA52HxokMjb90tV7%FYTT4KX!uRls%wi]HFAN@!!KUF5ndbr]9IQ($0c8t4rAyRrexk]xqIe#Mx[t6(TWXEHQ^IVvZXE9V1a%FNUSQIi4A!c5QtrFwrs^cUCf4vr)xPysxCPDQbpurOz]@D[iUBKrUYPUhTY[C#TwSB8exbM*3S7dByz#aTz0vz6r7NR)j!Rlb$S#00RKo!XAjLXz1VzK!EHwNphW%l@339tl5YLHTnf[iE@*Cl&jikKH@L5eJ)S#CRNG!JKC1I6(kfNt5CMlTZA8svhn^NxD0NxMk(BxNFw3o*Is2Z#JLW5wk%Es92!03b)oDM%V2b4QwWKudv(kPoMW%r[4@DKHk4q$%r&%VOD3[))3X1BimnmnuCUDXrhasPj3OF7*XtMD2t9AJg%&d0urxjyzU%)gS)UrAfRs]&BHOg!884kk#J%Mv6sehukAHevB88Ab(PYy*kJ(Gl@bNYTK^gnfbrqtI&^Bb@XjPh&Ul60fPEm4@p&O#gZnk*UMV@WHiC)3KpdBX1C3lXmklFvNIk!G118y#%oD[*YJ*jZkJdpki$5P@yzeujUNbARfiQ#F(OpIycJYyg4&T!&RM$4v(bjjK*5TVnw93dfP*@)6ZxEXIOR15Bb0pHLF(Z1RXBZR)lMY4g^qm1Rb[6dip835f@hp#pMwgE1PLdy*Sb11nOuGFHgfkf*!UcL]87CJvF13[Z1otcGGdg(7#a8fIzj3pTAYj@))hzl%pDCGjFW1*kNh6]N@QK1d&XUP8F^$91az#Aofq6jrkOAqbPemhyKxPr@a1HEQo3OD3*3)5@%pK$rTOX0!%$5gF#LYu%lL&ASZ*elnc$[YdH1xyby2H6Yme@l4lgxeg#C5bgNZbFbLKijI675VG#*)tEyl&FnxxwYd9DznRl5y08^YsA3T50dMBp8sNZ3Lou5tHjq6HcOYq2s@$H4^@$[%[y^i&qRk7K!a(NX@7Aulj)zOEnLObLbLm@FjH0J$fq5!L0BVV0lTcaKQtFdwYCu%&2y&8h*7^$4)F(rY14rPCNEs3Q)4!XhxP8(*6p3@LS$yy)0jDkbLnVmNKUMz877lV#6Hi!01Y6@Ex(FVHeOAdnv&jCKvbNU)q&NU3r8V2YZL0grAxDbZ!1[qHZ4th%UfQ9UqF(2npC8KNv9TS!&1P1QU71QJJ3S&dK93sCr%sT7[65A5mXB0(7tk8rC93L[8CtxsA@5Q$V!uyd2OE]DJ[twx!yM9v2XH*@!eK45%GyFaTH@y5NshqN2nNO@eEJc%#5d[sgrH8Qbn@afks]eNXvJEHio6KQwz7rvwvVYYHBpCf)2GSZANPn5frpgAAxBK7ki2hTb8CU7lHq2CTbLNemVzsox%f#Y@mhC1AL4dGzGt%u(zmV1O3&Wtf1eAn(S&4o8)CbHrRXZq9)UNV#2MI4B$c[yC@3k]4nESknwHW^NtMlN!37X&Z&WtQ3u&K6WeWxU%C4PweQm4NJK*dLKoigkSfEcwM1Vz67muzXu)bFT%7Q8lE8Ow0wkhL!hEfz6@wSVV[sI4pNJewGykBu*](G[$*2YkSt)DMk#sLJp1yjQvJFLzxp3JYTp^RVcHg54lG7odLjN5sZgcw81zYuNjUH5pN&Fsq62^1WhZ9EP2hlbL*fTu*M2F1xYuSmy#vpKXf^9ZgjJUw[*v)X*[InXQd]ckrqYfIu^jZDSrZpQC!w)ijuCxFY7O8CZoCGLsqbA3*5rzY(^UF54(@%26ei#(Yo)z*FnmneYj)p6RKC*11O!Nosj*QJ!g6)aCEnoa1n^A7g&yJ18SQE8X8MVLg!YKB3uG!9B4JHK(E3jPkYRTu8ozy$&$nspKCPt#J$X1WAmMM28pLAec9#Ptm1KBErNkfYI*ZLC41E9&N&7p2%%viQAGCRbR$q1#1@sD4!nD8e3SUy3tp^]Erb3nMLsCB5e5(VzLymWrzeH2q9ERL25Tr7I8AILm3mtWu1j2vi*yjNhn8)jquq0vQLD*7*lRS4fUBY0aif7Mz@FxsQNEC9DDgUASRFYBIfE$Mu5H!%%[NymRXOO4fgPsZGf[MMT!yHhPAfsAHmXI3U6d5[Qw^lE31R&1#ea(tQROS&xm#pV8#M6B3Uv5I9Y6Kq2Q)CKhBVqHAKXY6&c&m&uwDZpbpsSRETL1yyc)w11%BTttz1JAiXF^N^owrLD3Q!tliFaCVNXG^D8#40Uh5gmwf3V(JPhfl(#oZBXjz!PzL[Q#bxQnK!opS&eDJ22r&0f!n*TN!hr$XTWblMTh5fN^opzj87KHtY@f!*a1Pu4TMBhcOwAw5Qp6]qvZzUOWFkH1k7^%wgsBCkWj8Y@PKuHYk$lM$[CN9yL7QhTt8Qa0$CcyiXMXCwckc45Igkc2eugFplLbCIj[&EhvLn&kzgAI*j^0ST6GSII@ck@fn8(L17)jsX)#z8W[mTemNc8oPr&l2hl9302qI$NJR)$)dTET8UKsC7]metz$$9ZY&rQ$GVc^FYY]0UN7kYj[wnp*rtQy$P9YmAOekq^i&Yr3GiaO2Ee2&hIQDdcBmrxpex17F3tjFzgYR!dewizm27DzM%ZRm%AJyC3#ZzCY8t!sg$)Bg66Kq)LInaznNhvDd7i*$FTDQQKHSkKmU9myngPW)eivvvct1qfjoH8$goig3N9oRpc%edlKrHWdS9b73ggib@l0D$2F!dm%#cPBew[&j20[PK%#L$%&jQXjGXBnFkIghhAnk^fQyb9HIKumzt&OSe^9Aqt!xB7^]g$nC&4zkc#c&LNM#J*D3s0&X(27yzeQHVT)gKui9Y)VJp^CUd2WknDA8l%uourSnajsS(c9Z2RbU7JneS@49OMbP6wYyfcF!4xzWq3d&6PpAQ3*%0M[U0zZ5R)pXL!wF26H]YR[X3vgr0p@Zz^XriECZM)5&&e)7Rf$EZBhlhbOlivWARbV9i^^8py!l9XpnyaRCiGv#q$tUWom$kVZ6$9OI9sTC[I7j*pE2xbTwOnw%nuljK!60svfz7IoGUU2csFVg[W8%#N[0O0^fX&iuUA7CX1OWHjIvTQs5gePM2zOfIHkqBwLJ3qqZnAAp*bKEAQphjj*#s*$R54UKqeZ#wGO6$Ff$qNO1(mlU[ohBmPNEyk2U)u8ceb&*)5X9%@zcTNFISqP^V3*kqq#h#XXkLAeDYC[PBpbxrJ^piOIfE^)uyZ6ThjUgdF#yh!AsukGWv8KKU(Yl&Yke&fo@rw1HSM$RImO40wjePO&oYOE#XEZ7G@Y@gwU6Oj10Q&Dng8hTa#kK4lYB@7*R8K5(D9P#X8GAx1f8ro5jirw6$D861hT8bi%jFvHmE0(2jSEJz!L(LoYr7Ga^b0v(N2tj#)ED6iSgg^CDgM!$MSEE74fJwSa7NKT58RFClFg8JMcrUfdXAUMg33XhHOBSbnpk!Q2FD)kz8^M(p@T(FhME196EKGvF(FJB3Jq(ab3p%PPuSYbedtgfJk&NFN@lJOzjM[S5DWii%ypU)HS7]Y)CgOdbtsFD0jv4QJ5m!e3xuDR(WP8Ic#IQ1Vr)IdxJdILDcd3*lbAsB!o9*E[PtEVL3@yAb7P9iO28eK2nh$WE',
            'rule_name': 'ctt->ctt',
            'src_db_uuid': ' 1B1153F6-DAD9-BC39-888A-A743FCC208E5',
            'tgt_db_uuid': ' D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'tgt_type': 'oracle',
            'db_user_map': {
            'CTT': 'CTT',},
            'rule_uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.modifySyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'modifySyncRules', body)

    def testDescribeSyncRulesHasSync(self):
        a = Auth(username, pwd)
        body = {
            'offset': '0',
            'limit': 10,
            'row_uuid': 'd9AEe7eD-BD9d-d332-83CA-A78924b7dfde',
            'search': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesHasSync(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesHasSync', body)

    def testDescribeSyncRulesFailObj(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'rule_uuid': '5bA6fA95-818D-E3c2-Ab81-8F2337b4f4Bc',
            'search': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesFailObj(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesFailObj', body)

    def testDescribeSyncRulesLoadInfo(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesLoadInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesLoadInfo', body)

    def testDeleteSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'DBED8CDE-435D-7865-76FE-149AA54AC7F7',],
            'type': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.deleteSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'deleteSyncRules', body)

    def testListSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'group_uuid': '',
            'where_args': {
            'rule_uuid': '',},
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listSyncRules', body)

    def testListSyncRulesStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'ACCf9F05-Ccd6-8Ccf-6EB8-4FE1663A0D74',
            '3A541667-1c82-f9c5-A485-cE488Dca688B',],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listSyncRulesStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listSyncRulesStatus', body)

    def testDescribeSyncRulesMrtg(self):
        a = Auth(username, pwd)
        body = {
            'set_time': 1,
            'type': '',
            'interval': '时间间隔',
            'set_time_init': '',
            'rule_uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesMrtg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesMrtg', body)

    def testDescribeSyncRulesIncreDdl(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': '10',
            'rule_uuid': 'EaAEff59-eB80-EbB7-9719-30f7DBa918C0',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRulesIncreDdl(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRulesIncreDdl', body)

    def testDescribeSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'A923A558-b41F-Cb40-C95D-CB3fefcAE79b',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        syncRules = SyncRules(a)
        r = syncRules.describeSyncRules(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSyncRules', body)

    def testListObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listObjCmp', body)

    def testCreateObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'obj_cmp_name': 'test',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'cal_table_recoders': 1,
            'cmp_type': 'user',
            'rule_uuid': '751A03F5-C97D-645B-82B2-316A5D198528',
            'db_user_map': {'src_user':'dst_user'},
            'policies': '',
            'policy_type': 'periodic',
            'one_time': '2019-05-27 16:07:08',
            'repair': 1,
        }
        
        syncRules = SyncRules(a)
        r = syncRules.createObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'createObjCmp', body)

    def testDeleteObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.deleteObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'deleteObjCmp', body)

    def testDescribeObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        syncRules = SyncRules(a)
        r = syncRules.describeObjCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeObjCmp', body)

    def testListObjCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'DA4EFDEe-35Ae-db5c-7af6-CDDBBcb5F24D',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listObjCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listObjCmpResultTimeList', body)

    def testDescribeObjCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '1c7583E4-24eB-57c7-fa5a-c9A66D49BDc1',
            'start_time': '',
            'limit': 1,
            'offset': '',
            'search_value': '',
            'BackLackOnly': 0,
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeObjCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeObjCmpResult', body)

    def testListObjCmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listObjCmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listObjCmpStatus', body)

    def testDescribeObjCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '5ed66EbF-BAE8-acDA-9A7A-Cde6fbdB65FC',
            'time_list': [],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeObjCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeObjCmpResultTimeList', body)

    def testListObjCmpCmpInfo(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_value': '',
            'usr': 'I2',
            'filed': '',
            'uuid': '',
            'start_time': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listObjCmpCmpInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listObjCmpCmpInfo', body)

    def testCreateObjFix(self):
        a = Auth(username, pwd)
        body = {
            'obj_fix_name': 'test',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'rule_uuid': '751A03F5-C97D-645B-82B2-316A5D198528',
            'obj_map': [{
            'type': 'owner.name',},{
            'type': 'owner.name',},],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.createObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'createObjFix', body)

    def testDescribeObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'fA2fB1fa-BAef-eaB5-EfA9-42Fed0Edd4dC',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        syncRules = SyncRules(a)
        r = syncRules.describeObjFix(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeObjFix', body)

    def testDeleteObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuids': 'E46d4a32-98Cb-DdF3-674b-1Dd1cbA15ad1',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.deleteObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'deleteObjFix', body)

    def testListObjFix(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listObjFix', body)

    def testDescribeObjFixResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'df3Ad2fe-C784-8F8c-43AF-C809765Ef5f4',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeObjFixResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeObjFixResult', body)

    def testListObjFixStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listObjFixStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listObjFixStatus', body)

    def testCreateTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_name': 'ctt->ctt',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'cmp_type': 'user,table,db',
            'db_user_map': '{"CTT":"CTT"}',
            'filter_table': '[用户.表名]',
            'db_tb_map': '表映射',
            'dump_thd': 1,
            'rule_uuid': '4Cb7bcc7-5beB-969B-2c6A-38C5C6e4EEDd',
            'polices': '"0|00:00',
            'policy_type': 'one_time',
            'concurrent_table': [
            'hh.ww',],
            'try_split_part_table': 0,
            'one_time': '2019-05-27 16:07:08',
            'repair': 0,
            'fix_related': 0,
        }
        
        syncRules = SyncRules(a)
        r = syncRules.createTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'createTbCmp', body)

    def testDescribeTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '2F1BD5F2-0969-dCAE-2CB2-DAC5beDac99D',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        syncRules = SyncRules(a)
        r = syncRules.describeTbCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeTbCmp', body)

    def testDeleteTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuids': 'bDd3FB96-27D7-fD97-8bcF-cE61CCa289F9',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.deleteTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'deleteTbCmp', body)

    def testListTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listTbCmp', body)

    def testListTbCmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '1dcF478c-5112-fAd1-33c1-E8DD5eeC4FDc',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listTbCmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listTbCmpStatus', body)

    def testListTbCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listTbCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listTbCmpResultTimeList', body)

    def testDescribeTbCmpResuluTimeList(self):
        a = Auth(username, pwd)
        body = {
            'time_list': '2CE8c95F-9AC8-EFeF-c4Eb-6c0EAD62cAbE',
            'uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeTbCmpResuluTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeTbCmpResuluTimeList', body)

    def testDescribeTbCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'DD3BDbd9-4ec0-FD5e-dDc9-e68A7df21222',
            'start_time': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeTbCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeTbCmpResult', body)

    def testDescribeTbCmpErrorMsg(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'dEceDa3c-BFbD-A44D-f861-657eC256D0F5',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeTbCmpErrorMsg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeTbCmpErrorMsg', body)

    def testDescribeTbCmpCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeTbCmpCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeTbCmpCmpResult', body)

    def testCreateBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '7404A6e4-fEeD-7E4f-C5B1-0C5ee1bB8db2',
            'start_val': 1000,
            'scan_ip': [
            'c01D7F86-A631-b79f-E2AA-7ccb7f2bE851',
            'c01D7F86-A631-b79f-E2AA-7ccb7f2bE851',
            'c01D7F86-A631-b79f-E2AA-7ccb7f2bE851',],
            'hosts': [{
            'ip': '192.168.12.200',
            'password': '',},],
            'use_ip_sw': 1,
        }
        
        syncRules = SyncRules(a)
        r = syncRules.createBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'createBkTakeover', body)

    def testDescribeBkTakeover(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        syncRules = SyncRules(a)
        r = syncRules.describeBkTakeover(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeBkTakeover', body)

    def testDeleteBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'uuids': 'b7B91Be1-CE58-C0B2-F27d-8EbCdAE3bDA4',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.deleteBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'deleteBkTakeover', body)

    def testDescribeBkTakeoverResult(self):
        a = Auth(username, pwd)
        body = {
            'bk_takeover_uuid': 'D23C8781-7Bed-dFA0-CAdb-eF0279AE8B62',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeBkTakeoverResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeBkTakeoverResult', body)

    def testListBkTakeoverStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listBkTakeoverStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listBkTakeoverStatus', body)

    def testListBkTakeover(self):
        a = Auth(username, pwd)
        body = {
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listBkTakeover()
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listBkTakeover', body)

    def testCreateReverse(self):
        a = Auth(username, pwd)
        body = {
            'reverse_name': '',
            'rule_uuid': '7CfFfB84-77c6-dcef-B950-F5Ab5d5e2589',
            'node_uuid': '41CDDE6F-e6A2-7324-fbdd-Be965eDf3cbF',
            'start_scn': 1,
        }
        
        syncRules = SyncRules(a)
        r = syncRules.createReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'createReverse', body)

    def testDeleteReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        syncRules = SyncRules(a)
        r = syncRules.deleteReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'deleteReverse', body)

    def testDescribeReverse(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '86313AA4-aefe-D3fE-B8F1-CAef1F1C9AFf',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeReverse', body)

    def testListReverse(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listReverse', body)

    def testListReverseStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '022cfAE6-dbce-F8F2-fdeA-61cCffb3b274',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listReverseStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listReverseStatus', body)

    def testStopReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'a6F31B7A-ee1f-41B5-fD2c-41554e1Cba94',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.stopReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'stopReverse', body)

    def testRestartReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'F5b1fEDE-C8bF-bCDd-E4d1-de05c581514F',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.restartReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'restartReverse', body)

    def testDescribeSingleReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '743ca3a5-9D5e-A51C-1c43-ABe3C6CebEbE',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeSingleReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeSingleReverse', body)

    def testDescribeRuleSelectUser(self):
        a = Auth(username, pwd)
        body = {
            'db_uuid': '6CDE730D-ad5d-A37e-cf70-bafCdaEd16bd',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeRuleSelectUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeRuleSelectUser', body)

    def testDescribeRuleZStructure(self):
        a = Auth(username, pwd)
        body = {
            'tab': '4e806F9C-cCb4-f8f6-39f3-54b64aCDd28a',
            'user': '',
            'db_uuid': '5fDb001F-6fC1-CEB2-eF08-fc59DDcf5eC9',
            'lv': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeRuleZStructure(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeRuleZStructure', body)

    def testListRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '',
            'date_end': '',
            'type': 1,
            'module_type': 1,
            'query_type': 1,
            'rule_uuid': 'B306c9e5-dcCC-9253-E5aE-7e38aAFc9dCc',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listRuleLog', body)

    def testDescribeRuleTableFix(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '253CeD3E-4Cc2-f77c-6759-7FBE2f7ABd3c',
            'tab': [],
            'fix_relation': 0,
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeRuleTableFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeRuleTableFix', body)

    def testListRuleSyncTable(self):
        a = Auth(username, pwd)
        body = {
            'row_uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listRuleSyncTable(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listRuleSyncTable', body)

    def testListRuleIncreDml(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': '10',
            'rule_uuid': 'cBc5BeF6-A34d-fa9b-dAAb-c30Aa995EeA3',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listRuleIncreDml(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listRuleIncreDml', body)

    def testDescribeRuleGetFalseRule(self):
        a = Auth(username, pwd)
        body = {
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeRuleGetFalseRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeRuleGetFalseRule', body)

    def testDescribeRuleGetScn(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'B35F1b98-DA4f-FEbA-221f-005dCC13BC25',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeRuleGetScn(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeRuleGetScn', body)

    def testListRuleLoadReport(self):
        a = Auth(username, pwd)
        body = {
            'type': 'sec',
            'start_time': '',
            'end_time': '',
            'limit': 10,
            'offset': 0,
            'uuid': '1d2F6Fed-DAC6-FE94-A6cB-5Ab55415E9fd',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listRuleLoadReport(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listRuleLoadReport', body)

    def testListRuleLoadDelayReport(self):
        a = Auth(username, pwd)
        body = {
            'type': 'sec',
            'start_time': '',
            'end_time': '',
            'limit': 10,
            'offset': 0,
            'uuid': '1d2F6Fed-DAC6-FE94-A6cB-5Ab55415E9fd',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.listRuleLoadDelayReport(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'listRuleLoadDelayReport', body)

    def testDescribeRuleDbCheck(self):
        a = Auth(username, pwd)
        body = {
            'src_db_uuid': '',
            'dst_db_uuid': '',
        }
        
        syncRules = SyncRules(a)
        r = syncRules.describeRuleDbCheck(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'describeRuleDbCheck', body)

    def testResumeSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '',
            'scn': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.resumeSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'resumeSyncRules', body)

    def testStopSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '',
            'scn': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.stopSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'stopSyncRules', body)

    def testRestartSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '',
            'scn': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.restartSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'restartSyncRules', body)

    def testStartAnalysisSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '',
            'scn': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.startAnalysisSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'startAnalysisSyncRules', body)

    def testStopAnalysisSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '',
            'scn': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.stopAnalysisSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'stopAnalysisSyncRules', body)

    def testResetAnalysisSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '',
            'scn': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.resetAnalysisSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'resetAnalysisSyncRules', body)

    def testStopAndStopanalysisSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '',
            'scn': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.stopAndStopanalysisSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'stopAndStopanalysisSyncRules', body)

    def testRestartObjFix(self):
        a = Auth(username, pwd)
        body = {
            'obj_fix_uuids': '33E2BD5a-3bB8-Bc72-4Be9-ff9157ddfAD4',
        }

        syncRules = SyncRules(a)
        r = syncRules.restartObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'restartObjFix', body)

    def testStopObjFix(self):
        a = Auth(username, pwd)
        body = {
            'obj_fix_uuids': '33E2BD5a-3bB8-Bc72-4Be9-ff9157ddfAD4',
        }

        syncRules = SyncRules(a)
        r = syncRules.stopObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'stopObjFix', body)

    def testStopTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': 'DAD4dECC-2eED-6c37-e16e-018DDe7fFfad',
            'operate': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.stopTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'stopTbCmp', body)

    def testRestartTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': 'DAD4dECC-2eED-6c37-e16e-018DDe7fFfad',
            'operate': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.restartTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'restartTbCmp', body)

    def testStopBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'bk_takeover_uuids': 'Be227bF2-1553-edeC-9993-B4071D73c8Cb',
            'operate': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.stopBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'stopBkTakeover', body)

    def testRestartBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'bk_takeover_uuids': 'Be227bF2-1553-edeC-9993-B4071D73c8Cb',
            'operate': '',
        }

        syncRules = SyncRules(a)
        r = syncRules.restartBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'restartBkTakeover', body)

    def testDownloadLog(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
            'type': 1,
            'module_type': 1,
            'date_start': 1,
            'date_end': 1,
        }

        syncRules = SyncRules(a)
        r = syncRules.downloadLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'SyncRules', 'downloadLog', body)


if __name__ == '__main__':
    unittest.main()
