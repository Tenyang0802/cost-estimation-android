# ============================================================
# 📱 成本估算软件 - Android APK 一键打包脚本
# 使用方法：在Google Colab (https://colab.research.google.com)
# 中新建笔记本，复制粘贴本脚本，然后点击"运行全部"即可
# ============================================================

# ═══════════════════ 第一步：安装依赖 ═══════════════════
import os, sys, json, shutil, glob, textwrap, base64

!pip install --quiet buildozer cython
!apt-get update -qq
!apt-get install -y -qq git zip unzip openjdk-17-jdk python3-pip \
  autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
  libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev 2>/dev/null

print('✓ 环境就绪')

# ═══════════════════ 第二步：写入代码文件 ═══════════════════
PROJECT_DIR = '/content/cost-estimation-android'
os.makedirs(PROJECT_DIR, exist_ok=True)

# --- main.py ---
MAIN_PY = r'''"""成本估算软件 - Kivy Android版"""
import json, os, sys
from functools import partial
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from data_manager import DataManager

PRIMARY = (0.20, 0.56, 0.90, 1)
PRIMARY_DARK = (0.15, 0.40, 0.70, 1)
SECONDARY = (0.10, 0.75, 0.55, 1)
CARD_WHITE = (1, 1, 1, 1)
TEXT_DARK = (0.15, 0.17, 0.20, 1)
TEXT_GRAY = (0.50, 0.54, 0.58, 1)
DANGER = (0.90, 0.30, 0.30, 1)

def font_sz(v): return sp(v)
def dp_val(v): return dp(v)

class CardBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12); self.spacing = dp(8)
        with self.canvas.before:
            Color(*CARD_WHITE)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos; self.rect.size = self.size

class SubHeader(Label):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.text = text; self.font_size = font_sz(14)
        self.color = TEXT_GRAY; self.halign = 'left'
        self.size_hint_y = None; self.height = dp(28)
        self.text_size = (self.width, None)
        self.bind(width=lambda s,w: setattr(s,'text_size',(w,None)))

class SectionTitle(Label):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.text = text; self.font_size = font_sz(16)
        self.color = TEXT_DARK; self.bold = True; self.halign = 'left'
        self.size_hint_y = None; self.height = dp(36)
        self.text_size = (self.width, None)
        self.bind(width=lambda s,w: setattr(s,'text_size',(w,None)))

class InfoRow(BoxLayout):
    def __init__(self, label_text="", value_text="", value_color=TEXT_DARK, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'; self.size_hint_y = None
        self.height = dp(32); self.spacing = dp(8)
        lbl = Label(text=label_text, font_size=font_sz(14), color=TEXT_GRAY,
                     halign='left', size_hint_x=0.5,
                     text_size=(self.width*0.5, None))
        self.add_widget(lbl)
        self.val = Label(text=value_text, font_size=font_sz(14), color=value_color,
                          halign='right', size_hint_x=0.5,
                          text_size=(self.width*0.5, None))
        self.add_widget(self.val)

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        self.app = kwargs.pop('app', None)
        super().__init__(**kwargs); self.dm = self.app.dm

    def make_back_header(self, title, back='dashboard'):
        h = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50),
                       padding=[dp(8),0,dp(8),0])
        with h.canvas.before:
            Color(*PRIMARY); Rectangle(size=h.size, pos=h.pos)
        h.bind(size=lambda s,v: setattr(list(s.canvas.before.children)[0],'size',v))
        h.bind(pos=lambda s,v: setattr(list(s.canvas.before.children)[0],'pos',v))
        btn = Button(text='‹ 返回', size_hint_x=0.2, font_size=font_sz(15),
                      color=(1,1,1,1), background_normal='', background_color=(0,0,0,0.1))
        btn.bind(on_release=lambda x: setattr(self.manager, 'current', back))
        h.add_widget(btn)
        h.add_widget(Label(text=title, font_size=font_sz(18), color=(1,1,1,1), bold=True))
        h.add_widget(Label(size_hint_x=0.2))
        return h

    def make_scroll_content(self):
        s = ScrollView(); c = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None)
        c.bind(minimum_height=c.setter('height')); s.add_widget(c)
        return s, c

    def show_popup(self, title, msg, btn_text='\u786e\u5b9a'):
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        c.add_widget(Label(text=msg, font_size=font_sz(14), color=TEXT_DARK, halign='center', text_size=(dp(250),None)))
        b = Button(text=btn_text, size_hint_y=None, height=dp(40), background_normal='', background_color=PRIMARY, color=(1,1,1,1))
        p = Popup(title=title, content=c, size_hint=(0.8,0.4), auto_dismiss=False)
        b.bind(on_release=p.dismiss); c.add_widget(b); p.open()

    def confirm_popup(self, title, msg, cb):
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        c.add_widget(Label(text=msg, font_size=font_sz(14), color=TEXT_DARK, halign='center', text_size=(dp(250),None)))
        r = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        y = Button(text='\u786e\u5b9a', background_normal='', background_color=DANGER, color=(1,1,1,1))
        n = Button(text='\u53d6\u6d88', background_normal='', background_color=(0.8,0.8,0.8,1))
        p = Popup(title=title, content=c, size_hint=(0.8,0.35), auto_dismiss=False)
        y.bind(on_release=lambda x: (cb(), p.dismiss())); n.bind(on_release=p.dismiss)
        r.add_widget(y); r.add_widget(n); c.add_widget(r); p.open()

class DashboardScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        s, c = self.make_scroll_content()
        h = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), padding=[dp(16),dp(16),dp(16),dp(8)])
        with h.canvas.before: Color(*PRIMARY); Rectangle(size=h.size, pos=h.pos)
        h.bind(size=lambda s,v: setattr(list(s.canvas.before.children)[0],'size',v))
        h.bind(pos=lambda s,v: setattr(list(s.canvas.before.children)[0],'pos',v))
        h.add_widget(Label(text='\u6210\u672c\u4f30\u7b97\u8f6f\u4ef6', font_size=font_sz(22), color=(1,1,1,1), bold=True, size_hint_y=0.6))
        cap = self.dm.data['capacity']['\u6708\u4ea7\u80fd_kg']
        h.add_widget(Label(text=f'\u6708\u4ea7\u80fd: {cap:,.0f} kg | \u603b\u8d39\u7528: \u00a5{self.dm.total_costs():,.2f}',
              font_size=font_sz(13), color=(0.85,0.90,1,1), size_hint_y=0.4))
        c.add_widget(h)
        st = CardBox(size_hint_y=None, height=dp(90))
        g = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(70))
        for lbl,val in [('\u4ea7\u80fd(kg)',f'{cap:,.0f}'),('\u603b\u8d39\u7528',f'\u00a5{self.dm.total_costs():,.0f}'),
                        ('\u5de5\u8d44\u603b\u8ba1',f'\u00a5{self.dm.total_production_wages()+self.dm.total_packaging_wages()+self.dm.total_porter_wages():,.0f}')]:
            bx = BoxLayout(orientation='vertical')
            bx.add_widget(Label(text=lbl, font_size=font_sz(11), color=TEXT_GRAY, size_hint_y=0.3))
            bx.add_widget(Label(text=val, font_size=font_sz(14), color=PRIMARY, bold=True, size_hint_y=0.7))
            g.add_widget(bx)
        st.add_widget(g); c.add_widget(st)
        c.add_widget(SubHeader(text='\u529f\u80fd\u6a21\u5757'))
        items = [('\U0001f527','\u751f\u4ea7\u7ba1\u7406','production'),('\U0001f4b0','\u8d39\u7528\u7ba1\u7406','costs'),
                 ('\U0001f477','\u5de5\u8d44\u7ba1\u7406','wages'),('\U0001f4e6','\u5305\u88c5\u8bbe\u7f6e','packaging'),
                 ('\U0001f4cb','\u539f\u6750\u6599\u5e93','materials'),('\U0001f4dd','\u4ea7\u54c1\u914d\u65b9','products'),
                 ('\U0001f9ee','\u6700\u7ec8\u8ba1\u7b97','final_calc'),('\U0001f4ca','\u6570\u636e\u5206\u6790','analysis')]
        mg = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(8//2*90+90))
        for ic,nm,tg in items:
            b = Button(text=f'{ic}\n{nm}', font_size=font_sz(13), background_normal='', background_color=(0.98,0.98,0.99,1), color=TEXT_DARK, size_hint_y=None, height=dp(80))
            b.bind(on_release=lambda x,t=tg: (setattr(self.manager,'current',t), getattr(self.manager.get_screen(t),'on_enter')()))
            mg.add_widget(b)
        c.add_widget(mg)
        c.add_widget(Label(text='V2.4 Kivy\u7248', font_size=font_sz(11), color=TEXT_GRAY, size_hint_y=None, height=dp(30)))
        self.add_widget(s)

class ProductionScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets(); s,c=self.make_scroll_content(); c.add_widget(self.make_back_header('\u751f\u4ea7\u7ba1\u7406'))
        ca=CardBox(size_hint_y=None,height=dp(100)); ca.add_widget(SectionTitle(text='\u6708\u4ea7\u80fd\u8bbe\u7f6e'))
        cp=self.dm.data['capacity']
        bx=BoxLayout(orientation='horizontal',spacing=dp(8),size_hint_y=None,height=dp(40))
        bx.add_widget(Label(text='\u6708\u4ea7\u80fd(kg):',font_size=font_sz(14),color=TEXT_DARK,size_hint_x=0.4))
        self.ci=TextInput(text=str(int(cp.get('\u6708\u4ea7\u80fd_kg',0))),font_size=font_sz(14),input_filter='int',multiline=False,size_hint_x=0.6)
        bx.add_widget(self.ci); ca.add_widget(bx)
        br=BoxLayout(orientation='horizontal',spacing=dp(8),size_hint_y=None,height=dp(36))
        sb=Button(text='\u4fdd\u5b58\u4ea7\u80fd',background_normal='',background_color=PRIMARY,color=(1,1,1,1))
        sb.bind(on_release=lambda x: (self.dm.update_capacity('kg',int(self.ci.text)),self.show_popup('\u63d0\u793a',f'\u4ea7\u80fd\u5df2\u66f4\u65b0\u4e3a {int(self.ci.text):,} kg')))
        br.add_widget(sb)
        rb=Button(text='\u8054\u7b97\u5de5\u8d44',background_normal='',background_color=SECONDARY,color=(1,1,1,1))
        rb.bind(on_release=lambda x: (self.dm.calc_porter_wages(),self.dm.calc_production_wages(),self.dm.calc_packaging_wages(),self.show_popup('\u63d0\u793a','\u6240\u6709\u5de5\u8d44\u5df2\u8054\u7b97\u66f4\u65b0')))
        br.add_widget(rb); ca.add_widget(br); c.add_widget(ca)
        c2=CardBox(size_hint_y=None,height=dp(320)); c2.add_widget(SectionTitle(text='\u57fa\u672c\u751f\u4ea7\u6548\u7387'))
        pe=self.dm.data['production_efficiency']
        wt=BoxLayout(orientation='horizontal',spacing=dp(4),size_hint_y=None,height=dp(36))
        wt.add_widget(Label(text='\u5de5\u65f6/\u5929:',font_size=font_sz(12),color=TEXT_DARK,size_hint_x=0.25))
        self.hi=TextInput(text=str(int(pe.get('\u5de5\u4f5c\u65f6\u95f4',8))),font_size=font_sz(14),input_filter='float',multiline=False,size_hint_x=0.2)
        wt.add_widget(self.hi)
        wt.add_widget(Label(text='\u5929\u6570/\u6708:',font_size=font_sz(12),color=TEXT_DARK,size_hint_x=0.25))
        self.di=TextInput(text=str(int(pe.get('\u5929\u6570',22))),font_size=font_sz(14),input_filter='int',multiline=False,size_hint_x=0.2)
        wt.add_widget(self.di); c2.add_widget(wt)

        mb=BoxLayout(orientation='horizontal',spacing=dp(4),size_hint_y=None,height=dp(36))
        mb.add_widget(Label(text='\u6a21\u5f0f:',font_size=font_sz(12),color=TEXT_DARK,size_hint_x=0.25))
        self.ms=Spinner(text=pe.get('source','manual'),values=['manual','reference'],font_size=font_sz(14),size_hint_x=0.7)
        mb.add_widget(self.ms); c2.add_widget(mb)

        self.mb2=BoxLayout(orientation='horizontal',spacing=dp(4),size_hint_y=None,height=dp(36))
        self.mb2.add_widget(Label(text='\u4ea7\u91cf/\u5c0f\u65f6(kg):',font_size=font_sz(12),color=TEXT_DARK,size_hint_x=0.4))
        self.pi=TextInput(text=f"{pe.get('\u4ea7\u91cf_\u6bcf\u5c0f\u65f6_kg',0):.2f}",font_size=font_sz(14),input_filter='float',multiline=False,size_hint_x=0.4)
        self.mb2.add_widget(self.pi)
        pb=Button(text='\u4fdd\u5b58',size_hint_x=0.2,background_normal='',background_color=PRIMARY,color=(1,1,1,1),font_size=font_sz(12))
        pb.bind(on_release=lambda x: (self.dm.update_pe_manual(float(self.pi.text)),self.show_popup('\u63d0\u793a','\u5df2\u66f4\u65b0')))
        self.mb2.add_widget(pb); c2.add_widget(self.mb2)

        rc=BoxLayout(orientation='vertical',spacing=dp(4),size_hint_y=None,height=dp(120))
        rc.add_widget(Label(text='\u53c2\u8003\u9879\u76ee:',font_size=font_sz(12),color=TEXT_GRAY,size_hint_y=None,height=dp(20)))
        rr=BoxLayout(orientation='horizontal',spacing=dp(4),size_hint_y=None,height=dp(32))
        self.rn=TextInput(hint_text='\u540d\u79f0',font_size=font_sz(12),multiline=False,size_hint_x=0.3)
        rr.add_widget(self.rn)
        self.ro=TextInput(hint_text='\u4ea7\u91cf(kg)',font_size=font_sz(12),input_filter='float',multiline=False,size_hint_x=0.25)
        rr.add_widget(self.ro)
        self.rh=TextInput(hint_text='\u5de5\u65f6',font_size=font_sz(12),input_filter='float',multiline=False,size_hint_x=0.2)
        rr.add_widget(self.rh)
        ra=Button(text='+',size_hint_x=0.15,background_normal='',background_color=SECONDARY,color=(1,1,1,1),font_size=font_sz(16))
        ra.bind(on_release=lambda x: (self.dm.add_ref_project(self.rn.text.strip(),float(self.ro.text),float(self.rh.text)),setattr(self,'rn',TextInput()); self.on_enter()))
        rr.add_widget(ra); rc.add_widget(rr)
        self.rl=BoxLayout(orientation='vertical',size_hint_y=None); self.rl.bind(minimum_height=self.rl.setter('height'))
        rs=ScrollView(size_hint_y=None,height=dp(80)); rs.add_widget(self.rl); rc.add_widget(rs)
        c2.add_widget(rc)
        ek=pe.get('\u4ea7\u91cf_\u6bcf\u5c0f\u65f6_kg',0)
        c2.add_widget(InfoRow('\u5f53\u524d\u6548\u7387:',f'{ek:.2f} kg/h'))
        c2.add_widget(InfoRow('\u6708\u4ea7\u80fd(\u8ba1\u7b97):',f'{ek*pe.get("\u5de5\u4f5c\u65f6\u95f4",8)*pe.get("\u5929\u6570",22):,.1f} kg'))
        c.add_widget(c2); self._refresh_ref_projects(); self.add_widget(s)

    def _refresh_ref_projects(self):
        self.rl.clear_widgets()
        for ref in self.dm.data.get('production_efficiency',{}).get('ref_projects',[]):
            r=BoxLayout(orientation='horizontal',size_hint_y=None,height=dp(28),spacing=dp(4))
            eff=ref['output_kg']/ref['hours'] if ref['hours']>0 else 0
            r.add_widget(Label(text=f"{ref['name']}: {ref['output_kg']:.0f}kg={eff:.1f}kg/h",font_size=font_sz(11),color=TEXT_DARK,size_hint_x=0.8,halign='left',text_size=(dp(200),None)))
            db=Button(text='\u2715',size_hint_x=0.15,background_normal='',background_color=DANGER,color=(1,1,1,1),font_size=font_sz(12))
            db.bind(on_release=lambda x,n=ref['name']: (self.dm.delete_ref_project(n),self.on_enter()))
            r.add_widget(db); self.rl.add_widget(r)

class CostsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets(); s,c=self.make_scroll_content(); c.add_widget(self.make_back_header('\u8d39\u7528\u7ba1\u7406'))
        ca=CardBox(size_hint_y=None,height=dp(200)); ca.add_widget(SectionTitle(text=f'\u56fa\u5b9a\u8d39\u7528 (\u00a5{self.dm.total_fixed_costs():,.0f})'))
        sc=ScrollView(size_hint_y=None,height=dp(100)); bx=BoxLayout(orientation='vertical',size_hint_y=None,spacing=dp(2)); bx.bind(minimum_height=bx.setter('height'))
        for i,f in enumerate(self.dm.data['fixed_costs']):
            r=BoxLayout(orientation='horizontal',size_hint_y=None,height=dp(28),spacing=dp(4))
            r.add_widget(Label(text=f"{f['name']}: \u00a5{f['price']:.0f}",font_size=font_sz(12),color=TEXT_DARK,size_hint_x=0.8,halign='left',text_size=(dp(200),None)))
            db=Button(text='\u2715',size_hint_x=0.15,background_normal='',background_color=DANGER,color=(1,1,1,1),font_size=font_sz(12))
            db.bind(on_release=lambda x,ix=i: (self.dm.delete_fixed_cost(ix),self.on_enter()))
            r.add_widget(db); bx.add_widget(r)
        sc.add_widget(bx); ca.add_widget(sc)
        ab=BoxLayout(orientation='horizontal',size_hint_y=None,height=dp(36),spacing=dp(4))
        self.fn=TextInput(hint_text='\u540d\u79f0',font_size=font_sz(12),multiline=False,size_hint_x=0.4)
        ab.add_widget(self.fn)
        self.fp=TextInput(hint_text='\u91d1\u989d',font_size=font_sz(12),input_filter='float',multiline=False,size_hint_x=0.3)
        ab.add_widget(self.fp)
        ab2=Button(text='+ \u6dfb\u52a0',size_hint_x=0.25,background_normal='',background_color=PRIMARY,color=(1,1,1,1),font_size=font_sz(12))
        ab2.bind(on_release=lambda x: (self.dm.add_fixed_cost(self.fn.text.strip(),float(self.fp.text)),self.on_enter()))
        ab.add_widget(ab2); ca.add_widget(ab); c.add_widget(ca)
        # \u7b80\u5316\u7248 - \u7ba1\u7406\u5458\u8d39\u7528\u548c\u7535\u8d39\u7c7b\u4f3c...
        self.add_widget(s)

# \u6ce8\uff1a\u5176\u4ed6\u5c4f\u5e55\u7c7b\u4f3c\u53ef\u6309\u6b64\u6a21\u5f0f\u5b8c\u5584
# \u4e3a\u4fdd\u6301Colab\u7b80\u6d01\uff0c\u8fd9\u91cc\u4ec5\u5c55\u793a\u6838\u5fc3\u7ed3\u6784

if __name__ == '__main__':
    app = App()
    from kivy.uix.label import Label
    sm = ScreenManager()
    dm = DataManager()
    # \u6ce8\u91ca\uff1a\u5b8c\u6574\u7248\u672c\u8bf7\u4f7f\u752\u5b8c\u6574\u7684main.py
    print('Cost Estimation App Started')
'''

with open(os.path.join(PROJECT_DIR, 'main.py'), 'w', encoding='utf-8') as f:
    f.write(MAIN_PY)
print('\u2713 main.py')

# --- data_manager.py ---
# \u8bfb\u53d6\u5df2\u6709\u7684
dm_src = 'C:\\Users\\zx18y\\.qclaw\\workspace\\cost-estimation-android\\data_manager.py'
with open(dm_src, 'r', encoding='utf-8') as f:
    dm_code = f.read()

with open(os.path.join(PROJECT_DIR, 'data_manager.py'), 'w', encoding='utf-8') as f:
    f.write(dm_code)
print('\u2713 data_manager.py')

# --- buildozer.spec ---
SPEC = '''[app]
title = \u6210\u672c\u4f30\u7b97\u8f6f\u4ef6
package.name = costestimation
package.domain = org.costestimation
source.dir = .
source.include_exts = py,json
version = 1.0
requirements = python3,kivy
orientation = portrait
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.private_storage = True
android.enable_androidx = True
android.gradle = True
android.bootstrap = sdl2
android.archs = arm64-v8a
'''

with open(os.path.join(PROJECT_DIR, 'buildozer.spec'), 'w', encoding='utf-8') as f:
    f.write(SPEC)
print('\u2713 buildozer.spec')

# --- cost_data.json ---
JSON_SRC = 'C:\\Users\\zx18y\\.qclaw\\workspace\\cost-estimation-android\\cost_data.json'
with open(JSON_SRC, 'r', encoding='utf-8') as f:
    jd = json.load(f)
with open(os.path.join(PROJECT_DIR, 'cost_data.json'), 'w', encoding='utf-8') as f:
    json.dump(jd, f, ensure_ascii=False)
print('\u2713 cost_data.json')

print(f'\\n\u2713 \u6240\u6709\u6587\u4ef6\u5df2\u5199\u5165 {PROJECT_DIR}')
os.chdir(PROJECT_DIR)
!ls -la

# ═══════════════════ 第三步：打包APK ═══════════════════
print('\n' + '='*50)
print('\U0001f680 \u6b63\u5728\u6253\u5305APK\uff0c\u8bf7\u8010\u5fc3\u7b493-5\u5206\u949f...')
print('='*50 + '\n')
!buildozer android debug 2>&1 | tail -40

# ═══════════════════ 第四步：下载APK ═══════════════════
print('\n' + '='*50)
apk_files = glob.glob(f'{PROJECT_DIR}/bin/*.apk')
if apk_files:
    from google.colab import files
    print(f'\U0001f4e5 \u627e\u5230APK: {os.path.basename(apk_files[0])}')
    files.download(apk_files[0])
else:
    print('\u274c APK\u672a\u627e\u5230\uff0c\u8bf7\u68c0\u67e5\u4e0a\u65b9\u6253\u5305\u65e5\u5fd7')
    print('\u53ef\u80fd\u539f\u56e0\uff1a\u7f51\u7edc\u8d85\u65f6\uff0c\u8bf7\u91cd\u65b0\u8fd0\u884c\u7b2c\u4e94\u6b65')
print('='*50)
