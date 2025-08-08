
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.active.v20200720.OracleRule import OracleRule
# from info2soft.active.v20200722.OracleRule import OracleRule
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


class OracleRuleTestCase(unittest.TestCase):

    def testDescribeRuleDbCheckMult(self):
        a = Auth(username, pwd)
        body = {
            'db_uuid': [],
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeRuleDbCheckMult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeRuleDbCheckMult', body)

    def testDescribeSyncRulesObjInfo(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'rule_uuid': '1993ed2C-72cC-cFCB-8BC3-E7da46CAF7bF',
            'usr': '',
            'sort': '',
            'sort_order': '',
            'search': '',
        }

        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesObjInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesObjInfo', body)

    def testDescribeSyncRulesDML(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': '10',
            'usr': '',
            'rule_uuid': 'e7a05Dab-8ffC-fEdf-8eBE-7761bdEb0AFc',
            'sort_order': 'asc',
            'search': '',
            'sort': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesDML(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesDML', body)

    def testDescribeSyncRulesProxyStatus(self):
        a = Auth(username, pwd)
        body = {
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesProxyStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesProxyStatus', body)

    def testCreateOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': 'ctt->ctt',
            'src_db_uuid': ' 6C4AEF37-6496-6DCD-E085-DD640001E4EC',
            'tgt_db_uuid': ' 1C5F3C4B-7333-9518-7349-9712BC9ED664',
            'tgt_type': 'oracle',
            'db_user_map': {
            'CTT': 'CTT',},
            'row_map_mode': 'rowid',
            'map_type': 'user',
            'table_map': [{},],
            'dbmap_topic': '',
            'sync_mode': 1,
            'start_scn': '',
            'full_sync_settings': {
            'keep_exist_table': 0,
            'keep_table': 0,
            'load_thd': 1,
            'ld_dir_opt': 0,
            'his_thread': 1,
            'try_split_part_table': 0,
            'concurrent_table': [
            'hello.world',],
            'dump_thd': 1,
            'clean_user_before_dump': 0,
            'existing_table': 'drop_to_recycle',
            'sync_mode': 0,
            'start_scn': '',},
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
            'tgt_extern_table': '',
            'max_ld_mem': '',},
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
            'ignore_foreign_key': 0,
            'table_delay_load': [],
            'merge_track': '',
            'fill_lob_column': '',
            'keep_seq_sync': '',
            'gen_txn': '',
            'encrypt_switch': 1,
            'encrypt_type': 1,
            'encrypt_key': '',
            'table_change_info': 1,
            'message_format': '',
            'json_format': '',
            'run_time': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',
            'jointing': {
            'table': '',
            'op': 'append',
            'content': [],},},
            'bw_settings': {
            'bw_limit': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',},
            'biz_grp_list': [],
            'kafka_time_out': '7$4RPuy&^I!D[AXsN[*FP)0@ye%yp^TG[WOpegC]SLb#eTZEwz5gec7%nLH6TZuHMhtPHAVOL0h8]4y2Q@vbnlIDId[FJ8VMAtwTEnuxL%BS2v82G5N[3FS4NQEBvMdXyN[PkFBS2wdqShJ8#jXJy^hRp6qwFMBLAg[xrHFK(7&#A6FtTp81i&HD&vSz$x@gKJ!CSK@1h[70Zj%(4mmwTi]nNVPZAr6)SN8*aps7y3mRoak[iV]KM4u^SHUAAR8dk!YXV*#Qz5K%B20@J9ewY%4w)xOzP#VIt!FP#(3ojnc6V0F99%rX0N[0Q!dYHQps^R3#NeZi2f6H^dbEsXJ%18S4IuZmwCUHbvCI0ln^royf3H0gOpsb]lJb%bmg62YZ9UY5&W&UvkyrSSyDPlKBt2R)Eh5LavIQcsntBz0x5[DA0@@%4]jN!1V9X2V&k^(&BUR#M0os@FAU[s@b9TuA9dw6m[&JCxD$%)4vJAE0CL0i!Dkwu2fL&KCNrq^RsmO#m9%4yOoW2tuSY4TFOVapqrnz1SqzNmJYlUcBwWhW#AN5NTDLf*WUR)wCdgp2qpQ)NqRLFM*1XQh#zYEVo$Tb!S1$Qz!^I&@ib3X]G%2uYfB3@X8#UNNKl8t!&Euen^y$ws2##m4Ko257C^cLRU)Zo7vH(g6r5EZlx9IA*O2v[KTfc*48Z$^(gy($C2jymNgrtg*4IqVPzOL*sX(H3@JGh*43ot)YiXk(N[&ek^&Syd*0QIw[$%Qa7^8FJN!qc&ss*[(]uU0&h2C9V4[cEbj8@^x4Dp0Gpr7&!N7f5bAx2P*s8kU*)67q1SEon*[kOrmx0BHhswud[*^%uwwv(FgV*UWuE*[GwLDHzM#HDw6VNhHTnzW%4EW4wxxSYje(b[RRIkoB]wh&UuX8QB!n2A&DhGUc*H$Zh3!9Dqe^sDgShXKOEsYBD7O5LuYYn15^c6nSJTNN#spr)Urlfo)Gvw%yGc(hGZ!OFC8NI$!$M5TliOs@ko4fsNFA4QqpjItpI04enKNVqad&EKo*lBlfrK5y4tm#i$4Xp00*prBAcMP&^SV%pLH^A&25gUT^mrpv[Q1N4UQLX3818jqEU8Y7W^MF)Vtnk)SxMXBrEqLv&y![uOo#9v!2V0l2rqDvY(SxfEEE8J#%[XbHtSEx%CbF]VmxHe!0zADKFVlfqp6@7jhZfiVzPOWVbZlEd5(Ohvu$qflrM8fGZfZRP8rmdQ@nB^5J*eVNnF1&PJ0ykVb19D@C(A[eI^p1s6W9lvx59HqE)f3@sQP[60XPncFFd2WZ&AxBPtr0DyLa0X(QDWD2I#C9uXI%lbW[ag4VkDATqu1Anhc8TJL0AhYSf^9uWW*NKcV1uB3fbcR%64R)Qb27f*q8hR5co0*lc6rUf$&UTxM397BwbM5y*7%xRKql@B22528IN@*Zja(dSz^agphkXqR@w&!JB3v*CG2S$p4WeV[&AM)lo4nES2Can1j#nMS0T(DOM!$I)EyYxDGO5[2&3kJy7KVRSNkDo^#HG5O1QH5%yR!q6#6Y^F4Zs3)Vl9ZcYbvF@Wfz)!cLWad4FMV3I0$FHMcPy34nY^1V[)RAFKRta(ENC$TTtnX6SsdHQ94i1mq3*5DoMbAxNq2eqY5TMCr&lmoODJZ1G6ce17O%[[dZcZ%o9eFrIYc1uIjzjIskKxO0MW2(2hRQx2mnJK%Q*@CIDY!zUW4kGm[7QxOp*Q&pJ7RrQPVict0OoVM&5D[ufJQKsRT!]qIR1q1uO$JpKhSFiATgDF)wy^kd$qjIHbci6iB85O37OyDFTGJEw[Q#6EtVBVl0J8XCZ3HPUvrK#0mzSL&DbDYR@kZcovyI9CFEzqQ0pPJUyJi4XKwie[KUXfoh^^nKm5oTxu$fxd3N5GvrCQyXyFB^D1!Tr[knak2!qEzZox2Bqlw1$EGLDi6Zw7LNyID7&ggXPut!)q)(PH8XS]il@tMm7YnYiD0)nDDSp(Lt(cwR6f%j#qrKz#W[y!SFLZX^b&Wi[FT42MeWBytR7xnt#elMLIB&hv4kJ9n)SJPm8Wl(I4bsXR68B^u^MSKRAP8&6ji2&pZEGUmdi]wnXiU2AhGkGa2UP$lfF2&nM$EK$[NDg89aC]U4I$uyEycB7LBLXc#TS)x$M6Q8fmU7$FLkmtv0xGJkU]t68CFV6pkzo6*pHDG&9)S#uqR4C!nvYkb4Dwo0tPzbz$leqemp)0zkJV(odosVIf&gecPQFs$9n([HjeM^WOQmfsMj]S#B2^r26PbZB3DdFLkHrMxbwH42w@@tPeoPxn0nS%8%(3p5W#oLO4kZPI6BSne1(3j@CyxL4SX!9iaW1clEFGqADj&wM48qQ(WyVES][DevJo(4^iXMA5meg*e3v8)AlLSQ7wh%pVk9Y!XgqiHQtvX%KioVQ0cxqRHXZs3HkDOTzY4nX1IwhI^dYjbPyk!]H&DJ*jK9DQ8H@)S@z3ft&uajRec9yTctesu8G#cqqjdQ%d*FE#br4O)jPAM0dGg[QIC#avp$Aoj$JKK^UjYy@2j3ro[^nsMSAdnVqEygiUTnAZZXs^qv2L4GR)y%gL@@[(&)n11raMN*IY8E8zX)B&lG(JdALUcBT9OUdo4*YYIIk(A4%LDl8SO!Vluq0GD)aF*^Lz4OGh$DiN4Wgw&Y]Rd[GA)A04ybV*lm#jqodIMqifUt5pxEFfY0CPg$iH(ZlSFOc*EDbfIqU3$z0EF%Vdq*rXR8wFq9*^u^VW$U(XxyE@x5NJskWFltu%CqBCWZhyOtooOylQsJz)^EP3D4wrUVKetXqN8In)wR3]f^WOoOJidQGz*LzVQLsW(PBN0[!zUKzFqphp3KATeA%!r^DjSgscZlkEVV0lfzwgA&hQtyG4D#e3Xu(0hY^Co)k^FWJccMt!H0Mg@jpq683AI7ZH9$XyZmb&f[]4ArikP^hK6)qbrvjeHapiPT[^JaTJGPQz[JE!3I!kHuGiLRBP]2ePSbT6mfEMZAh##sf4bt@E8X*nO*kVr^MifGwX)YaR*sze33oWq7Oju1&W6cOvn$&U1CKRIBlROu]iru7q8$vI9vy#ny!&NmZBXQ#CDEDGL7[B$M#FFRL32M8bG0D0I6ylIZw72K#lM&BEtY#gC*l7uRA3WKn$CMsiXiU0S1qvm8c7WDv^sA@8#g#3uJ(JvR#@)r9X#qMZ5O2&tWmKwbnSj0VVZfS@X!1g$E9$V2iZN8[4soQp!kKxnK^%F$REwFZmq@ogMcsZ8Y2mD0ghm9$ms7pWto6G(Rs94Yq[i^3^JD48pyi3vLr0XbED7yEdkrFM@TmPoq58o37$Ic5nH@iIQE8BM)Y1tBSk(BXgE@AHxX!wuXzdH4!M4m)h)mw#RbDZ!iFonEOG[wVc4)[e[vCfsA#C92zMI!4)4D#KivRyccx$Ke%YE(DbJ2K(lIIq[B)yc7IYAEmA)jOEG*KczUQz5lkCABf@q[thUVpZYD]odHWtON6)$MwSSox%!Y*ga5J(#HLzI[5VrEUOA^)UMsiPfc[o2Ut]rndC$7SU!U91@T4]Bn^hmn1oVT&Mitz8Qn8n4$[o&zOkEeMENZT*PMhWZoJHxxFgABjQ@sRU3YqrkSV2eDxrG2RDx78)LI6Rp6okSgVLZtp(Dy37aMz5s%vQCQUL(Z6!tHR22&v2BMcBRsl6il9@wY9CS&gh6RnhKkquYrN&s6O)%ZPrJ9a3&Mt9u@kAOAvWmdI00D@5S5#Pq7OP8QWI6g6HHl31rx5B@v6eHdlpPCy%E$XQ&01S378Sz&ssGZsqk*caokIv$7Q!CmlW)z0qU^T&jVFHUQ5BWmkNLv)zgOMLMAEkEX7gv#diZ*NyAAZryTgnj)k#Y4!*mP7Sg(T]D8[[X!LEopK&2q)1@k1xelzogFl3rgLe6QpK3^znnkjyMIcAN*L#E@DJIFvILXLf%TuJF%COxpAf2AE29hZVDxn(7XgbQSb2g%uvEDpoR7Foaq1B*7l42NOPaOVoyuNK3718Vv#MrmocunWnDsdaZ&0mC6giLy)5yzY8gb!KUCANERi[1Bt%umYeHi%AWXniqhiK68K9k9ylAZ@c6J9j*rR*UvmR578)1RE^6c&AvchQ]1$i[fpe9yX$6iRFrkJcOPp($IsBk8^uB]mk[tG&c%UT0F7n0nFwLdI!baylUU!O)Ma%Gi97*c([ewz7UBkg(uo82k4VCQToHxr4P$DXscVO6pNAz8cW63^OHMB@f&Iu4k0B*f3I1!O!cqRkt&Z4uC2xm^vq1rYlyc1)HrRiHF5@mrfNTZP6tZWJkorX4H^n2BZdurpuKOPqe01$tJac@slK6#GzjlHJ@LSGyyXazBq5qtrslJOket%L@xxbUvuMKY9Gn*urA$^LDeF[$KkwCmy$6AApJt5)Kr1ZN)*Gfmf3(wEl4h773kfMson[YuLePBSKzDlUMm4HsENNCzY%7sJ#NIFNM%ojx^owzwJo%5SUEuLc5KI8Nsz6I[AiG(ET8xRJ%DGtS5lDFclT0@VJgRnszah^7hH5&d6Gsrb6BCin7UEBTtnnz6s#H[4!5OY^y]0bePp)V0vLI$IMoPfHDJWmQ[&@AzKvk(3tf0Mm]P@i]4)mTe@BVm*[o#TxMGt#gl6PkjOXA^*rV45%GKi^VmqUVVWJAQ4UzP4dh6ned(@v^Oq(&jiBY8jLRL2T8!F)7%HdH@ADk*Zd5l37Uc1ovJUlseYxrKrPR(MonY1GPPt9Pl2)WDvhX)fJ*RoBXnv$KWg6$]EM1@U3sJGT@8s(^Q&NIxWV9(]y*(#Fk]4og#zsA5IGW)g6uDfV*)m6CZ2!6pjCTZPRdKe1$wNBVCbYLjhZdQ(Q!U#6Vtfm*zDltZ6XbvzFe8WQPUXaAHVzYc2C3B#d8!k#bu1%P6(lsi)amCnbqVH1UD5vhfHyf(@&py27zLVka9hcigSi^M0WE3wXXG!WYonS3%RvaMiM1W5EI&2qwjOkN8MUaWEGsocu5VvE0&Gt34pCv#9E*Ow@)N!ahmnT$HSUlcAAJ241w3GBvOA(TvTHhhcDKT8$3RBq#@nJdCG2AjMc1TcXtB%WrZlJXR^89wb5rxf^dEVq&oBsabe86Ih(0sMaMsEAw)V7m(L&g7LSBO0Ch6eUC^X$#mv*7mx1$[sLit[pd3No$$mYRuJSmY4LpH1AdcgbRRODrE[ooJo7xcNO^MEkDCk%S&R7(nme)EveolXT6z1bB8dgrSyVi^)npyzjPY92H0oznC8zLqK&UUdGcp9Qc3Vcz*KY)25bf1NmELOh2lwQt%P*GSmhME6KbN72wlUaPQBUhy&N^IZ4g6zcNk$4udX77^wiRC29kCnF35mg23GxxQW)pKrBDIKXBHoS*QiB@7Z%TAlguLD(J$&I^fpKKWQs$0zEiDkOtVQtDYPFHlnRVrP1^cYzpZ*feW83#y&YHi$&4@G1My8C58)6a02&kNN9a@Knr*UGM0K7Umy)ES)nfdRTuU8Z8Kw!*xYsg&3V0@K5JSV#a&IL8isehBL$MzblOc$9D2[Zn#ANE61DqXU56t4yHEgzFmb1u#jL4czLIpnoy5RAi7mFwc9iNlL0v9BnvKmGD&HEhEI$bF9#woL50AuZMxWeef74nVmD*XO8UN4nc1gN5WDV7RA^bS^g!I^(cnUup764Su93HI7137NQZuuh9H^uOrG#YMlyb^tppEfUB)bcu531dmjJi5OEfDH3gExZ2fG(s$hPsD6CI!5ELfOCK0#zdXGbmO%n*Tl!!S%OfTxG(8)@6Q6Cyk@q3jd0%kFiZ@r!Pq6cJ*8HGOTZT7ee@50q7S%V(FKpSzA@CqRzo[%R8t1P!Jh$9QSb#%*REeUfrThjh@UukECbPk)7)9VQ2drEw3YP@EyMk7zt[lcn9GLUe2d&omUSZMCm[6!^4sX2qWRI7C5slfehUfmvdv52KT)Y*l02Re485ir8&xbnF*D$bc*WUB!g@cxC2wJY[obnNC@PFxoiAyyZLI1(ZE&mOIG*3#S7adwQk9T8m7CD&(wxgKL8zUM1MFz5A)ou01ERcEy)&USM#yqWMSAlVxBWmLpnqi3Ub2RqCh4S[*3ce8z2GFY45iDfFK)SThHbup*51rBzV0x5341lg#o%hopdCvtaEtjeGfhhoeh&oFAaRu#nbQ5wQJRFgEF3kh@q3p2kSZIgdcVNxphgl02I7b@!#2dQninPr)TRg*@gHVPxo#VdLw(BhElm3wGoATHh]2z7(fdVVo*lQ*JFkEHWlweQLPJHHAf1ZDU5o$JZA8ih8gv%Te*MQA]V&4b%[7VY2M*c1^#AXK8[l6Hlqll!*q24(h0vt)@H%Zp(&9skU(S%izk5pG4D&zU#z1hh[O92ssb6(FCQfh$Zi)0G9D[r)!#&]@%S2D713zGLpV%wZ(gsVy@liZVv#(NLtKD$J^9rTHS)1qmkR5KT1oj^xRI)D@f8z*fx%@o7jb(uGoJHYzHdKU72c^ONJp0M(wmi%fiPy[3)0Oi2SlNvHbxsI#SKrwLSJZq&p7K8T]ycRvt#tZN4]YQIDzfizFDZbl620pnoHhfAzRv$pG&t8HBQL7fnmlJxqcqoi(z!YQkIp$C[TT#OK25THkD@0[fZIfZfYal#Q1w*i8%u!ObrgAVk6w#57*io316MUW7IGQv&ytnRTuF@76nq)Sx[HQ#lMwgR)AnexK[&g2coCSUdhEfH0VvVRbHOhj9lR9l2f9ryl#XeQLnbf[J415E0JgKvLPL$gWt0VAv8zijay]]WZT]08SKNnr%tPGjhei3uS8ZwN2#TEeDAXGCFn%gjzkCjW9x0LPePB(BYEqoC(2L03AguTriDWMC]jMUIl30S@(BpdqFA[q*sqoh[6Xqnonmd*#v)x0svjvZC$lX#MMQON]W6ti(%Mi1z9Tm!tz38R!A!d@s$M2[T75S%aQ[Nc#uSeR3efxtZmg9G4r#*IsXjokN5!BXcUn0Qs@&2y[2lW&KY##In6(gTYhZ466jLjQ0Lb%ca!D7jK3Oc%!BaINe1@HmjLwzH3RzB*EP$vGLI1OQ(nPK5@7[Lk2[s8VN]dt*m*W()xly$WLaU94jF$N00CyvjPP@Uz!1Uf#fqMeXe2e747^]0!LCUAqKbrK5tK!ssxBMz)6VBUzgOrDn8yIeelM%uRUoTPwr@c6$26d]JjP83SSJ0ic7#5^k5ZAW@WulB3%8S$Z5U&Ur7^uSsA6G8HDtIWunpg@2dQ0xOx!8C*ePx&7%siNq!*pp0ycupGJIQ7#jXZ5#BHXF6Zlw^qC3H@CO$lsOOD3L&YiE1mzJb0(fwthX4(TmQxA&FBDdCOvcnRa$hcW8@Z2[$89wg9PDSAR9h&L^I!TU%Cf[mZ4IlFGTGG($gyfHpIW225t374Vdzt23p[zb#%X7@)8a2yi!QGi6TZMbC8TN51Z4l4Ad*[&u87$2Kw*iGyxJ&(!5C%ltJLWS9[hpPE2)LOmyDdt9^Ucl]gcoh^Qvz4oFEDx17NK8P&v1yCUCd7QexrplcSj8Mg5!hEZPLEdgu)[e%&P1n#h8)72F*Dn7xm9bSyRZ6hFivf1i6UA6I7kvK*HkqHMmZRxdRsxf39)RTP8rWn29(a3)ALkW]M6nAMfDPbL2YodVuqGyA1R$LeeN^k0Ed5(PwB5D8@pI7pj!m25Y(OL9*hwfNQWI3mo%RnLPllFlc)1DuE3oDIfxnd&dQ^Ti[56rKBT05XvFHq0U0dwf3rcwbz[DrkfSN4Z4()]43XT^qd2z%CAV2UAM2AbdoBeRhiQbvM*J#@[R)p9YTFLf(I!hGVMENm0My5G%Rb$7^vur4P12vk7ezZF6!UOF6]MRlO!1pH@edT9FgF)mXqQU1BG*PH%Zc4k[4g@yM[S6k@2HvHI7xR$P7CAZ6J!Bwrb*GM55jKDQsLMbk9VJ)loAVA%@%VOirHoCTxw7y3^%lfM3YCi!EUxBU@!mjxpV[OJ3jcV4YJG0!yo*oKtpTYA]oI$wCj&NyZ5PkD9p#z0JDZBr)X&]*^n$wX0NNe3qKATK8aN@6%*0@A6%mlKqSJHYHpJb$Rz0x54Nz&fXggy4ys2zmk(moY3[wruobyf8j2pgO@X&36QMT]E]%yn6petoK75IcAF(bIy&p3HB^nOJoneBHTDZTyhW9H80(]*QD%QEzi7pqX0GkqabBG%W6C#SxoM5kWO5)(yCM9i%PEYzqymSby&L[sShLXu3F5iEBlJSN4HkCVWZK#e@W4lFYxWRP$l^RYXc(AY2u(a%Tt([Lj9s$NT)Yed0$xn298if#0k6(ox3T[TfZ[shG3NH[j(vc7slx9$xG7GN2%4Y3jl03Q7N9bz1k$H*D)1iOW#SxfaLyZ@be7YG2mS*F4bvxDD4LlExM&IAP[Yk9GiDjzkMyHBsBrTN0Sr1*lCIhoQDUu^FU[QNbmzTR*lj#TqqgU2GyrIWAG72s#9446!B8TD@qnAb$h7f]HUuLoQqvez%q*7I7#JPx31jGe#AOtRtrlRc3WasRqYS9SBbMJhOhP@zbvtO2IoJGt84gB3Pil3yd*zQxqNkX1mOskg8ATN2kj^H3YZP6Hv![B9$3ey67q@EIBxwRtdjNNn[A[g$c9g^8Fz]y67L!S6tOfmMu@5cqw9lkkzgmuAO2TKzFoJHoUk04^ApMRwk5l#^d5(XIt5GotlR^!!YJrbBr&qaGtiSvjAvjo5rMwQk4*uFFh@eSlk0A*4Gf@A)OE7RK#Afm2*&MLTwn@Ru*4s852$J5W@7a[A4!)rh8FtdiF$m9kVKi96cHOU4[jlen!kWqP%CDJv*Ezl%X12&SOSm(1d(KDy8R[GMhLRec&t3zH@efmvaWZtBbww6HoOaN9VHv[Md&(P)YHZJscHx(1cvL0zVe1$x3@4sNS67)o1SgvQ9m3NwKmjcDRFH*FgFk!W#D3K%^eG7F2ZRbH8uv7QvAX1rQ&RU^Jb^2HFzgfwjiOW#s71^^cUGUPJ!oYSGPxCbX)t^Pu^01X0Z[f0[Pdle]wRO$^Ago@Uk#5tonz%d6L7O49CC8j3))OlZod)uYnhxd2dRGs12okbWEeFUD##Nem4Z3YkKbKft5A7Qed3QJzOn0I5isG1G]wM[j1XLc^aU^Qt$1OkTRe*Ib%OP!Ruo!JlP#L5x4)@Ka38uv]Y[mPQXWOf!6]M^3Zz7e(WxhcuvZL23$dW#*#K[f$jc@L[S6NGDLbiQo**bkGMY^Y6yEV3(6D6aw2ZsC]mbzu*Ph9rg[Quc&vBfpLCZV[)D^z31x#rd2FYm])iKPt2gqEbJ0P*TZ@1dO$Mk^a^V7PxtcUlegVjuvGuAU(nrAL2cV0w1FhdB37Z!23cU!W2oCrc&Wgw)sj6[wxLKwT4$CxWQw2G!(7u0DZx*HEMk@%!ZFXj!JmBcAX)^L4KU@a[v4#92E)ubdQ1(%6HgbO[Z48m#YrOo&3I$5LO[zW6fjJi*k^N0!C*alEJtn$p&95tQ1CbSI(OU[U@SVkWJX3jcn(LuyG])u!A[Qn[UauMAOf(nuxh*Y(Ye79iCIOPtc1*80Fi(RIvOGQnZ@4[Mmk#qGgz5IvGx71GML$BZY^l#tu7@#$d^Ri&NQ6^ObYF8xg*YjRf6(8u3lf*&E0jSDhP0kAuu8UXnqDP!@rx51)bpZjWslcDDNf#1*g&XYlfFI%csZ^r$*duO^o*t0fDJ7xQ[URUi4Lq^tYeJ^T)zbY)EgyMZaO(i%Zw*tQ4RZOBr4nLB4*Cpc#WWfCX77(Alu8^xE4508(qcOs3i^qtbisYlJ11R2#[F[6V4A#Zo(X5N)n#i4Y2^h@HT$%z2PJwJlAy2CYO%smnfJKSy1ZDVSoUXfCR*c4CjKJ^*s4!h190A4FXcr5o0BZ8NgX0f%WZroy9USF]6jqLC^&rCp)6*qctC#bqFJ%&q3Z#*G(oF^Sw9K@Q!$[Qq@o0i3SA8gpwXqIXxQOTcVi5JIIU2%P@GtvUc(8sY[sQi9oVHXYm2$UxSL!H7X#@qxDFb5Xy&ljJr(GLB[q5AxryK1l9%U3yJQn&(^MGejZbDU$g2iXx#UyXE@@z[R5!whHUsyT$32(rAxz5W*pFL8RzKGISA*1*zSG])Ca4%NwsSfeV8)bL^r5Dt[AoLi1#LnjYYY(%glCY9MFT!)cWMOMOPCSkLXbjkfJyrUTRP#2hXNRwZ2NeUumZ1dic$gWyjfOkmdlA@%EDf*lW#sMqDlplF1qo5xv@z3*btUo#bPrfv5gCn(7J3zSRw7J(BlOdXB0$)L7p0%QxHgEP3mkun^)BJrQ8IhMUcH2uF!Y0)%s^XPidb0Z8%[M]ScS*AIXtvXTRB!)pld*W@pVr6NHd3w*(*!TuDYQ1[Rx9i#uJ0I*e1H8Aj48kPLtHDo6j&KduB1W[nsknqh5s6YDWKWDaJQyataE9NDULvIrWk(O&@o^]5f%75sUZX%FyFHAd*BEI&^wZyO)kfP[1Q2pNZ7N%rtJux1gToDazslIZp7RsENFbibVgUnPBAk4bzKW(kdq)8F&fKyOEgtJi(Tibx31D*sx(PJ6Zb^fRVh@Wbi^3Ao8GNCG$d#JSQ]IU%B$AsuVEqq*#Zk&d$knqzQ7Ab6io)1xp#9zbN1b!x0y2Ch1x97N7QVNNoTe@)CF(A3#p%[z1Igb@QK6^Rd8xcEgZEQ@oSJAe6!ID*@rJdiJ&f2gHnOz9mgsVqNGDk(u(eWu^1&7#%dCs^gSIQXYeK1HEE6ML(8yt5CnI3hSM6uPmZu3NKuo3R4TqiCWyQUQ4t&(R&slgI$StyOE&USVOFlOrdh#Iv66PDc$s$eWH75F]ejk7]Rnw$Bjz3#N$nc1#HETr0CzHuk[E#ey0B4VSj%#$4jZPNIMdo@LDUxqjl67CrKy4JARJOXszbriY!4Ss8wu)@8smnk1dCndi&^Sjlw0BxSR7haL^u[lUqCAmeSsThjY*(]G^XrNXh9jj4PqFbJl(^2MvIARa7TluCkIH38us)XAExq%Xz7AlbYC6epo0YS6C!i@wSQkrKuPJPwBnKvd2khH(8Eck^J0o!M[!EP2wHv0&o4j15qmopV1LESv1h[m4oPWqvjjRyozwN4W#(9evQj$pn(xkK7semeN2wrlmyKQQqXMGxnv)3rG0KKLpr5jw$z8DMVvxc1dHr(bVPes%!2c1oTdGMRpGNgm[CXFW*p2IfTdb$L*KkLI0kQ$zc[S3B*6xd)Rju1pRdB@r1(ONY5HAm#o9%c5oSrmq*JkSPz]rq01oIYGdcFkau(gFhFhgTPxEt^i65muQ%&Vt)V#qEIaqJeauXUF1Ei8c@Qrog53ICQq)IKuTY@WeLxPqcnI5u)3R[4yGzezA61twMiTm&y4^YHmonnOJe[h5Zw[I!lg4oJJq5p$vRsckc]MfIV*z^!@]9vpHTsX^Bie)fP*1NQPN4C#u(cJ5gAJgmh4V67crxmr*O2ZZn]enZ^wmQ)q7]#3*$EF4aDeOG1XCyat*YgZc7)3RfO3JeLB&dQkYQwWFNJc0ES7EoAgvZH6[we@2%1I@4F%C9Y)HG&*x#QxFMUu$Wgw^L$MJvgDmE^$S@Ra4ILqXS5H!ufWaAslUirIN6QN^iPOebCg0*[Tt%1DPM9PpBiTJ$uiEh#v839ZdzcDYZkBc#1J5P*j41ktv$Ch)u(PjAZK6[t@jAAZz%DzseiR)MG6RcS5pxs2D4JIA[l7vV%l*q#(PadjZHWHRW7ltpHMwm&CLy3DByCxi&#KvIl75IzELVU*joZPvK!cBtpcwWzMkw*422&[O07tjYw]zNRlBk27UXn#chLpwv0DyEr[BTQK%p0xpYfPI#ssNd]LSfvpJQeVG%&u8*c!IxvEb#DP^W2#9jmr3bL!H&Xpu5suXJqJiIqwcs@FOpZtFFCXVn[l6J8zcnGv8ILtm$rQ4E]nMC3[dWrCHgXbNomNU7gVXsqEFG)Siw3h)IU02P@C&^rkXrNj6jFZp[x8C8O2ZLVcPPHrlbz6fvoDmhqI3ToQ0BNv![ZgB[R4tLVf8RGJ!$LS5PFI8xEIVDNWbLr^z2IAvuxRlJj20u@3kYVYOANK03HMFEfQJ!5mrUn&UgNkY',
            'part_load_balanceby_table': '',
            'kafka_message_encodingUTF-8': '',
            'kafka': [{
            'binary_codehex': '',},],
            'dml_track': [{
            'enable': '',
            'keep_deleted_row': '',
            'date_column': '',
            'time_column': '',
            'date_time_column': '',
            'op_column': '',
            'opv_insert': '',
            'opv_update': '',
            'opv_update_key': '',
            'opv_delete': '',
            'audit': '',
            'audit_prefix': '',
            'audit_appendix': '',
            'identity_column': 'AUTO_INCR',
            'load_date_column': '',
            'load_time_column': '',
            'load_date_time_column': '',},],
            'error_handling': {
            'load_err_set': 'continue',
            'drp': 'ignore',
            'irp': 'irpafterdel',
            'urp': 'toirp',
            'report_failed_dml': 1,},
            'save_json_text': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.createOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'createOracleRule', body)

    def testModifyOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'row_map_mode': 'rowid',
            'map_type': 'user',
            'table_map': [{},],
            'dbmap_topic': 'test1',
            'sync_mode': 1,
            'start_scn': '1',
            'full_sync_settings': {
            'keep_exist_table': 0,
            'keep_table': 0,
            'load_mode': 'direct',
            'ld_dir_opt': 0,
            'his_thread': 1,
            'try_split_part_table': 0,
            'concurrent_table': [
            'hello.world',],
            'dump_thd': 1,
            'clean_user_before_dump': 1,
            'existing_table': 's',
            'sync_mode': 1,
            'start_scn': '1',
            'load_thd': 1,},
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
            'table': '1',
            'user': 'user',
            'process': 'SKIP',
            'addInfo': '1',},],},
            'start_rule_now': 0,
            'storage_settings': {
            'src_max_mem': 512,
            'src_max_disk': 5000,
            'txn_max_mem': 10000,
            'tf_max_size': 100,
            'tgt_extern_table': '1',
            'max_ld_mem': '1',},
            'error_handling': {
            'load_err_set': 'continue',
            'drp': 'ignore',
            'irp': 'irpafterdel',
            'urp': 'toirp',
            'report_failed_dml': 1,},
            'table_space_map': {
            'tgt_table_space': '1',
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
            'ignore_foreign_key': 0,
            'table_delay_load': [{
            'table': '',
            'user': '',},],
            'keep_seq_sync': '1',
            'gen_txn': '1',
            'merge_track': '',
            'fill_lob_colum': '',
            'sync_lob': 1,
            'table_change_info': 1,
            'message_format': '',
            'json_format': '',
            'run_time': '',},
            'bw_settings': {
            'bw_limit': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',},
            'biz_grp_list': [],
            'part_load_balance': '12',
            'kafka_time_out': '12000',
            'rule_name': 'ctt->ctt',
            'src_db_uuid': ' 6C4AEF37-6496-6DCD-E085-DD640001E4EC',
            'tgt_db_uuid': '  1C5F3C4B-7333-9518-7349-9712BC9ED664',
            'tgt_type': 'oracle',
            'db_user_map': {
            'CTT': 'CTT',},
            'rule_uuid': 'F530FB0E-0208-9071-66D3-E595AE7D5A4C',
            'kafka': [{
            'binary_code': 'base64',},],
            'dml_track': [{
            'enable': 1,
            'urp': 1,
            'drp': 1,
            'tmcol': '1',
            'delcol': '1',},],
            'save_json_text': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.modifyOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'modifyOracleRule', body)

    def testDeleteOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
            'DBED8CDE-435D-7865-76FE-149AA54AC7F7',],
            'type': '',
            'force': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.deleteOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'deleteOracleRule', body)

    def testListSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': 'rule_name',
            'search_value': '',
            'group_uuid': '',
            'where_args': {
            'rule_uuid': 'BAbd22a3-8fb8-c5e2-9B36-8A13173d56db',},
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listSyncRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listSyncRules', body)

    def testDescribeSyncRules(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'F530FB0E-0208-9071-66D3-E595AE7D5A4C',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRules(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRules', body)

    def testResumeOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.resumeOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'resumeOracleRule', body)

    def testStopOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.stopOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopOracleRule', body)

    def testRestartOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.restartOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'restartOracleRule', body)

    def testStartAnalysisOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.startAnalysisOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'startAnalysisOracleRule', body)

    def testStopAnalysisOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.stopAnalysisOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopAnalysisOracleRule', body)

    def testResetAnalysisOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.resetAnalysisOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'resetAnalysisOracleRule', body)

    def testStopAndStopanalysisOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.stopAndStopanalysisOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopAndStopanalysisOracleRule', body)

    def testStopScheduleOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.stopScheduleOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopScheduleOracleRule', body)

    def testStartScheduleOracleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'rule_uuid': '552206c2-Ed85-6b51-6B21-42BFA6d9026d',
            'scn': '1',
            'all': 1,
        }

        oracleRule = OracleRule(a)
        r = oracleRule.startScheduleOracleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'startScheduleOracleRule', body)

    def testListRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '2018-12-23',
            'date_end': '1980-09-19',
            'type': -1,
            'module_type': -1,
            'query_type': 1,
            'rule_uuid': 'F530FB0E-0208-9071-66D3-E595AE7D5A4C',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listRuleLog', body)

    def testListSyncRulesStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listSyncRulesStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listSyncRulesStatus', body)

    def testListSyncRulesGeneralStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'EE992515-8DDb-9404-5eF7-F847422Ba8e3',
            'c23be9AF-E314-0e76-8CEC-E74BaFc329F0',],
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listSyncRulesGeneralStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listSyncRulesGeneralStatus', body)

    def testDescribeSyncRulesHasSync(self):
        a = Auth(username, pwd)
        body = {
            'offset': '0',
            'limit': 10,
            'row_uuid': 'b6Fddd9C-D515-6D2E-6CeC-96b1bF9FDe14',
            'search': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesHasSync(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesHasSync', body)

    def testDescribeSyncRulesFailObj(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'rule_uuid': 'afC2Ef54-996F-CCBB-e2F6-2d1877eFccAB',
            'search': '',
            'type': 1,
            'stage': 1,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesFailObj(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesFailObj', body)

    def testDescribeSyncRulesLoadInfo(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesLoadInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesLoadInfo', body)

    def testListRuleIncreDml(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': '10',
            'rule_uuid': 'cACDe7eF-bCf9-5d8c-b9fc-B5e991f4678a',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listRuleIncreDml(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listRuleIncreDml', body)

    def testListRuleSyncTable(self):
        a = Auth(username, pwd)
        body = {
            'row_uuid': '7FaEF546-e3e3-1760-673b-12B1cEbfeD71',
            'limit': 15,
            'offset': 1,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listRuleSyncTable(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listRuleSyncTable', body)

    def testDescribeRuleZStructure(self):
        a = Auth(username, pwd)
        body = {
            'db_uuid': 'A83Cc1A5-FAe2-C1aB-D58f-0272761c534A',
            'level': '',
            'type': '',
            'tab_name': '',
            'type_value': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeRuleZStructure(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeRuleZStructure', body)

    def testDescribeSyncRulesMrtg(self):
        a = Auth(username, pwd)
        body = {
            'set_time': 1,
            'type': '',
            'interval': '时间间隔',
            'set_time_init': '',
            'rule_uuid': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesMrtg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesMrtg', body)

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
        
        oracleRule = OracleRule(a)
        r = oracleRule.listRuleLoadDelayReport(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listRuleLoadDelayReport', body)

    def testDescribeSyncRulesIncreDdl(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': '10',
            'rule_uuid': 'CbcC8ee1-45dF-bDBc-fE6f-E6A6D7DF2E36',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSyncRulesIncreDdl(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSyncRulesIncreDdl', body)

    def testDescribeRuleDbCheck(self):
        a = Auth(username, pwd)
        body = {
            'src_db_uuid': '',
            'dst_db_uuid': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeRuleDbCheck(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeRuleDbCheck', body)

    def testDescribeRuleGetFalseRule(self):
        a = Auth(username, pwd)
        body = {
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeRuleGetFalseRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeRuleGetFalseRule', body)

    def testDescribeRuleSelectUser(self):
        a = Auth(username, pwd)
        body = {
            'db_uuid': 'AefceB68-6B69-d5a2-cCDb-F82635ecCCFD',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeRuleSelectUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeRuleSelectUser', body)

    def testDescribeRuleTableFix(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': 'F530FB0E-0208-9071-66D3-E595AE7D5A4C',
            'tab': [
            'I2.table',],
            'fix_relation': 0,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeRuleTableFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeRuleTableFix', body)

    def testDescribeRuleGetScn(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '8410B91E-2DDA-fda0-3e7d-bc729D91Dd2a',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeRuleGetScn(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeRuleGetScn', body)

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
        
        oracleRule = OracleRule(a)
        r = oracleRule.listRuleLoadReport(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listRuleLoadReport', body)

    def testListObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listObjCmp', body)

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
            'config': {
            'one_task': 'immediate',},
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.createObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'createObjCmp', body)

    def testDeleteObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            '11111111-1111-1111-1111-111111111111',],
            'force': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.deleteObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'deleteObjCmp', body)

    def testDescribeObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        oracleRule = OracleRule(a)
        r = oracleRule.describeObjCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeObjCmp', body)

    def testCmpStopObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        oracleRule = OracleRule(a)
        r = oracleRule.cmpStopObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpStopObjCmp', body)

    def testCmpRestartObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        oracleRule = OracleRule(a)
        r = oracleRule.cmpRestartObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpRestartObjCmp', body)

    def testCmpImmediateObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        oracleRule = OracleRule(a)
        r = oracleRule.cmpImmediateObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpImmediateObjCmp', body)

    def testCmpStopTimeObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        oracleRule = OracleRule(a)
        r = oracleRule.cmpStopTimeObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpStopTimeObjCmp', body)

    def testCmpResumeTimeObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        oracleRule = OracleRule(a)
        r = oracleRule.cmpResumeTimeObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpResumeTimeObjCmp', body)

    def testListObjCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'b0E8DBd1-64FF-534D-19C3-F3405f4bE5be',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listObjCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listObjCmpResultTimeList', body)

    def testDescribeObjCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'AcCcfeC8-7374-0Fd5-3dEa-b9da9AeCc7DB',
            'start_time': '',
            'limit': 1,
            'offset': '',
            'search_value': '',
            'BackLackOnly': 0,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeObjCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeObjCmpResult', body)

    def testListObjCmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listObjCmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listObjCmpStatus', body)

    def testDescribeObjCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '9D43d629-2c11-Ae39-8cEE-12a2198F9c0e',
            'time_list': [],
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeObjCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeObjCmpResultTimeList', body)

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
        
        oracleRule = OracleRule(a)
        r = oracleRule.listObjCmpCmpInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listObjCmpCmpInfo', body)

    def testCreateObjFix(self):
        a = Auth(username, pwd)
        body = {
            'obj_fix_name': 'test',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'obj_map': [{
            'type': 'owner.name',},{
            'type': 'owner.name',},],
            'obj_fix_uuid': '9Aad7B34-C2eA-af3F-64cf-5e7B6AECCCdB',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.createObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'createObjFix', body)

    def testDescribeObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'FcdBCAC6-bbEA-9cea-e1eF-9EbaA8Eb2F15',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        oracleRule = OracleRule(a)
        r = oracleRule.describeObjFix(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeObjFix', body)

    def testDeleteObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '49A4ffAF-8441-C85F-80Da-FC2C8C567bCA',
            'force': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.deleteObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'deleteObjFix', body)

    def testListObjFix(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listObjFix', body)

    def testRestartObjFix(self):
        a = Auth(username, pwd)
        body = {
            'obj_fix_uuids': '9db3722a-6A25-25e5-e3Cc-53582bd6fdED',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.restartObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'restartObjFix', body)

    def testStopObjFix(self):
        a = Auth(username, pwd)
        body = {
            'obj_fix_uuids': '9db3722a-6A25-25e5-e3Cc-53582bd6fdED',
        }

        oracleRule = OracleRule(a)
        r = oracleRule.stopObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopObjFix', body)

    def testDescribeObjFixResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'E335ED9F-6FCd-1d84-fcBe-153cFcE016D7',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeObjFixResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeObjFixResult', body)

    def testListObjFixStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listObjFixStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listObjFixStatus', body)

    def testCreateTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_name': 'ctt->ctt',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'cmp_type': 'user',
            'db_user_map': '{"CTT":"CTT"}',
            'filter_table': [
            'i2.test',],
            'db_tb_map': '{"ctt:ctt"}',
            'dump_thd': 1,
            'rule_uuid': '49eDe644-6cAe-3CAD-fC1d-3ef858BA557e',
            'polices': '"0|00:00',
            'policy_type': 'one_time',
            'concurrent_table': [
            'hh.ww',],
            'try_split_part_table': 0,
            'one_time': '2019-05-27 16:07:08',
            'repair': 0,
            'fix_related': 0,
            'config': {
            'one_task': '',
            'tab_cmp_fiter': [{
            'user': '',
            'table': '',
            'condition': '',},],
            'start_rule_now': 1,},
            'report_msg': 0,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.createTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'createTbCmp', body)

    def testDescribeTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'B8773e8b-8dA6-6CB2-eDEf-cd2892E66cc4',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        oracleRule = OracleRule(a)
        r = oracleRule.describeTbCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeTbCmp', body)

    def testDeleteTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '834f9BDc-aB2b-48A2-5d27-2A3e51Eb76Ed',
            'force': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.deleteTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'deleteTbCmp', body)

    def testListTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listTbCmp', body)

    def testListTbCmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '8Ab28B3A-6eaD-E2Bf-A8bc-7D7CdDe1c566',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listTbCmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listTbCmpStatus', body)

    def testStopTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': '5774f953-78d9-f3E1-bc50-B9bA9f2E01DB',
            'operate': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.stopTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopTbCmp', body)

    def testRestartTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': '5774f953-78d9-f3E1-bc50-B9bA9f2E01DB',
            'operate': '',
        }

        oracleRule = OracleRule(a)
        r = oracleRule.restartTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'restartTbCmp', body)

    def testCmpImmediateTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': '5774f953-78d9-f3E1-bc50-B9bA9f2E01DB',
            'operate': '',
        }

        oracleRule = OracleRule(a)
        r = oracleRule.cmpImmediateTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpImmediateTbCmp', body)

    def testCmpStopTimeTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': '5774f953-78d9-f3E1-bc50-B9bA9f2E01DB',
            'operate': '',
        }

        oracleRule = OracleRule(a)
        r = oracleRule.cmpStopTimeTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpStopTimeTbCmp', body)

    def testCmpResumeTimeTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': '5774f953-78d9-f3E1-bc50-B9bA9f2E01DB',
            'operate': '',
        }

        oracleRule = OracleRule(a)
        r = oracleRule.cmpResumeTimeTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'cmpResumeTimeTbCmp', body)

    def testListTbCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listTbCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listTbCmpResultTimeList', body)

    def testDescribeTbCmpResuluTimeList(self):
        a = Auth(username, pwd)
        body = {
            'time_list': '14F7A5d6-1d73-FC61-be2F-EbcC5Cf335f6',
            'uuid': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeTbCmpResuluTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeTbCmpResuluTimeList', body)

    def testDescribeTbCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': '2f56179a-f2cD-9f71-74d1-eEcbfA1BeD12',
            'start_time': '',
            'flag': 0,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeTbCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeTbCmpResult', body)

    def testDescribeTbCmpErrorMsg(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': '8B711a3d-A466-E4C1-9ccA-BcE9DeFD8bC4',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeTbCmpErrorMsg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeTbCmpErrorMsg', body)

    def testDescribeTbCmpCmpDesc(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'FDEB1968-cACE-Fa3b-794b-1d2b5FFFfFEf',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeTbCmpCmpDesc(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeTbCmpCmpDesc', body)

    def testDescribeTbCmpCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeTbCmpCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeTbCmpCmpResult', body)

    def testListBkTakeoveNetworkCard(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listBkTakeoveNetworkCard(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listBkTakeoveNetworkCard', body)

    def testCreateBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '2dC857d9-ff7A-cd5b-ad5b-984EccAE5A91',
            'type': 1,
            'enable_trgjob': 1,
            'enable_alter_seq': 1,
            'start_val': 10,
            'enable_attachip': 0,
            'net_adapter': '',
            'ip': '',
            'disable_trgjob': 1,
            'dettach_ip': 1,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.createBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'createBkTakeover', body)

    def testDescribeBkTakeover(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        oracleRule = OracleRule(a)
        r = oracleRule.describeBkTakeover(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeBkTakeover', body)

    def testDeleteBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'uuids': 'AB8293a3-3dEE-6b29-CD3F-98DCbe1bABAc',
            'force': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.deleteBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'deleteBkTakeover', body)

    def testDescribeBkTakeoverResult(self):
        a = Auth(username, pwd)
        body = {
            'bk_takeover_uuid': 'C63430e0-5AC7-EFcF-Be12-d1FabECB6E15',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeBkTakeoverResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeBkTakeoverResult', body)

    def testStopBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'bk_takeover_uuids': '2BF4aFac-9A3A-f352-caA5-8aee913f8AA6',
            'operate': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.stopBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopBkTakeover', body)

    def testRestartBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'bk_takeover_uuids': '2BF4aFac-9A3A-f352-caA5-8aee913f8AA6',
            'operate': '',
        }

        oracleRule = OracleRule(a)
        r = oracleRule.restartBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'restartBkTakeover', body)

    def testListBkTakeoverStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listBkTakeoverStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listBkTakeoverStatus', body)

    def testListBkTakeover(self):
        a = Auth(username, pwd)
        body = {
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listBkTakeover', body)

    def testCreateReverse(self):
        a = Auth(username, pwd)
        body = {
            'reverse_name': '',
            'rule_uuid': 'F530FB0E-0208-9071-66D3-E595AE7D5A4C',
            'start_scn': 1,
            'rowid_thd': 5,
            'row_map_mode': '"rowid"',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.createReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'createReverse', body)

    def testDeleteReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
            'force': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.deleteReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'deleteReverse', body)

    def testDescribeReverse(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': 'C1bdE82b-194e-6415-5DA5-71C8C85E34de',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeReverse', body)

    def testListReverse(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listReverse', body)

    def testListReverseStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': 'fDD8e834-19a6-FC1B-FFBF-55Bb630ABe1c',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listReverseStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listReverseStatus', body)

    def testStopReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'E3B62d58-474e-f266-edC5-be1af7B146Af',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.stopReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'stopReverse', body)

    def testRestartReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'bCBD8a2c-2cd2-1Ce4-4Daa-f6c4Bb3Dd1EB',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.restartReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'restartReverse', body)

    def testDescribeSingleReverse(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'dBcBAf7E-e1F5-F2d6-eA8A-B5f60F24f6Db',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.describeSingleReverse(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'describeSingleReverse', body)

    def testDownloadLog(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
            'type': 1,
            'module_type': 1,
            'date_start': 1,
            'date_end': 1,
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.downloadLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'downloadLog', body)

    def testListKafkaOffsetInfo(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '8F9cb942-156f-17aC-eCCa-CBc48cbCA91F',
        }
        
        oracleRule = OracleRule(a)
        r = oracleRule.listKafkaOffsetInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OracleRule', 'listKafkaOffsetInfo', body)


if __name__ == '__main__':
    unittest.main()
