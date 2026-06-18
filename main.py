"""
成本估算软件 - Kivy Android 版
全功能移植：14个功能模块，移动端友好界面
"""
import json
import os
import sys
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
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform, get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line

from data_manager import DataManager

# ======================== 颜色/主题方案 ========================
PRIMARY = (0.20, 0.56, 0.90, 1)       # #3390E6
PRIMARY_DARK = (0.15, 0.40, 0.70, 1)  # #2566B2
SECONDARY = (0.10, 0.75, 0.55, 1)     # #19BF8C
BG_LIGHT = (0.96, 0.97, 0.98, 1)      # #F5F7F9
CARD_WHITE = (1, 1, 1, 1)
TEXT_DARK = (0.15, 0.17, 0.20, 1)      # #262B33
TEXT_GRAY = (0.50, 0.54, 0.58, 1)     # #808A94
DANGER = (0.90, 0.30, 0.30, 1)        # #E64D4D
WARNING = (0.95, 0.67, 0.20, 1)       # #F2AC33


def font_sz(sp_val):
    """辅助函数，统一字体大小"""
    return sp(sp_val)


def dp_val(dp_val):
    """辅助函数，统一间距"""
    return dp(dp_val)


# ======================== 自定义Widget ========================
class CardBox(BoxLayout):
    """卡片容器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        with self.canvas.before:
            Color(*CARD_WHITE)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos,
                                         radius=[dp(8)])
        self.bind(size=self._update_rect, pos=self._update_rect)
        # 阴影效果（通过偏移矩形实现）
        with self.canvas.before:
            Color(0, 0, 0, 0.05)
            self.shadow = RoundedRectangle(
                size=(self.size[0], self.size[1] - dp(2)),
                pos=(self.pos[0], self.pos[1] - dp(2)),
                radius=[dp(8)])

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.shadow.pos = (self.pos[0], self.pos[1] - dp(2))
        self.shadow.size = (self.size[0], self.size[1] - dp(2))


class SubHeader(Label):
    """副标题"""
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_sz(14)
        self.color = TEXT_GRAY
        self.halign = 'left'
        self.valign = 'middle'
        self.size_hint_y = None
        self.height = dp(28)
        self.text_size = (self.width, None)
        self.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))


class SectionTitle(Label):
    """区域标题"""
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_sz(16)
        self.color = TEXT_DARK
        self.bold = True
        self.halign = 'left'
        self.valign = 'middle'
        self.size_hint_y = None
        self.height = dp(36)
        self.text_size = (self.width, None)
        self.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))


class ValueLabel(Label):
    """数据展示标签"""
    def __init__(self, text="", color=TEXT_DARK, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_sz(14)
        self.color = color
        self.halign = 'right'
        self.valign = 'middle'
        self.text_size = (self.width, None)
        self.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))


class InfoRow(BoxLayout):
    """带标签和值的一行信息"""
    def __init__(self, label_text="", value_text="", value_color=TEXT_DARK, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(32)
        self.spacing = dp(8)
        lbl = Label(text=label_text, font_size=font_sz(14),
                    color=TEXT_GRAY, halign='left', size_hint_x=0.5,
                    text_size=(self.width * 0.5, None))
        self.add_widget(lbl)
        self.val = Label(text=value_text, font_size=font_sz(14),
                         color=value_color, halign='right', size_hint_x=0.5,
                         text_size=(self.width * 0.5, None))
        self.add_widget(self.val)

    def set_value(self, text, color=TEXT_DARK):
        self.val.text = text
        self.val.color = color


# ======================== 主应用 ========================
class CostApp(App):
    def __init__(self):
        super().__init__()
        self.dm = DataManager()
        self.title = '成本估算'

    def build(self):
        self.icon = ''
        sm = ScreenManager(transition=SlideTransition(duration=0.2))
        sm.add_widget(DashboardScreen(name='dashboard', app=self))
        sm.add_widget(ProductionScreen(name='production', app=self))
        sm.add_widget(CostsScreen(name='costs', app=self))
        sm.add_widget(WagesScreen(name='wages', app=self))
        sm.add_widget(PackagingScreen(name='packaging', app=self))
        sm.add_widget(MaterialsScreen(name='materials', app=self))
        sm.add_widget(ProductsScreen(name='products', app=self))
        sm.add_widget(FinalCalcScreen(name='final_calc', app=self))
        sm.add_widget(AnalysisScreen(name='analysis', app=self))
        return sm


class BaseScreen(Screen):
    """基础屏幕类，提供导航栏和返回功能"""
    def __init__(self, **kwargs):
        self.app = kwargs.pop('app', None)
        super().__init__(**kwargs)
        self.dm = self.app.dm

    def make_back_header(self, title, back_target='dashboard'):
        """创建顶部导航栏"""
        header = BoxLayout(orientation='horizontal',
                           size_hint_y=None, height=dp(50),
                           padding=[dp(8), 0, dp(8), 0])
        with header.canvas.before:
            Color(*PRIMARY)
            Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda s, v: setattr(
            list(s.canvas.before.children)[0], 'size', v))
        header.bind(pos=lambda s, v: setattr(
            list(s.canvas.before.children)[0], 'pos', v))

        back_btn = Button(text='‹ 返回', size_hint_x=0.2,
                          font_size=font_sz(15), color=(1, 1, 1, 1),
                          background_normal='', background_color=(0, 0, 0, 0.1))
        back_btn.bind(on_release=lambda x: setattr(
            self.manager, 'current', back_target))
        header.add_widget(back_btn)

        title_lbl = Label(text=title, font_size=font_sz(18),
                          color=(1, 1, 1, 1), bold=True)
        header.add_widget(title_lbl)

        # 占位
        header.add_widget(Label(size_hint_x=0.2))
        return header

    def make_scroll_content(self):
        """创建可滚动内容区域"""
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical',
                            padding=dp(12), spacing=dp(8),
                            size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        scroll.add_widget(content)
        return scroll, content

    def make_input_row(self, label_text, input_widget):
        """带标签的输入行"""
        row = BoxLayout(orientation='horizontal',
                        size_hint_y=None, height=dp(40), spacing=dp(8))
        lbl = Label(text=label_text, font_size=font_sz(14),
                    color=TEXT_DARK, size_hint_x=0.35, halign='left',
                    text_size=(self.width * 0.35, None))
        row.add_widget(lbl)
        input_widget.size_hint_x = 0.65
        row.add_widget(input_widget)
        return row

    def show_popup(self, title, message, btn_text='确定'):
        """显示提示弹窗"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text=message, font_size=font_sz(14),
                                  color=TEXT_DARK, halign='center',
                                  text_size=(dp(250), None)))
        btn = Button(text=btn_text, size_hint_y=None, height=dp(40),
                     background_normal='', background_color=PRIMARY,
                     color=(1, 1, 1, 1))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4),
                      auto_dismiss=False)
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def confirm_popup(self, title, message, callback):
        """确认弹窗"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text=message, font_size=font_sz(14),
                                  color=TEXT_DARK, halign='center',
                                  text_size=(dp(250), None)))
        btn_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                            size_hint_y=None, height=dp(40))
        yes_btn = Button(text='确定', background_normal='',
                         background_color=DANGER, color=(1, 1, 1, 1))
        no_btn = Button(text='取消', background_normal='',
                        background_color=(0.8, 0.8, 0.8, 1))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.35),
                      auto_dismiss=False)
        yes_btn.bind(on_release=lambda x: (callback(), popup.dismiss()))
        no_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(yes_btn)
        btn_row.add_widget(no_btn)
        content.add_widget(btn_row)
        popup.open()


# ======================== 仪表盘 ========================
class DashboardScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()

        # 顶部标题区
        header = BoxLayout(orientation='vertical', size_hint_y=None,
                           height=dp(100), padding=[dp(16), dp(16), dp(16), dp(8)])
        with header.canvas.before:
            Color(*PRIMARY)
            Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda s, v: setattr(
            list(s.canvas.before.children)[0], 'size', v))
        header.bind(pos=lambda s, v: setattr(
            list(s.canvas.before.children)[0], 'pos', v))

        header.add_widget(Label(text='成本估算软件', font_size=font_sz(22),
                                 color=(1, 1, 1, 1), bold=True,
                                 size_hint_y=0.6))
        cap = self.dm.data['capacity']['月产能_kg']
        header.add_widget(Label(
            text=f'月产能: {cap:,.0f} kg | 总费用: ¥{self.dm.total_costs():,.2f}',
            font_size=font_sz(13), color=(0.85, 0.90, 1, 1),
            size_hint_y=0.4))
        content.add_widget(header)

        # 快速统计卡片
        stats = CardBox(size_hint_y=None, height=dp(90))
        stats_grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None,
                                 height=dp(70))
        labels = [
            ('产能(kg)', f'{cap:,.0f}'),
            ('总费用', f'¥{self.dm.total_costs():,.0f}'),
            ('工资总计', f'¥{self.dm.total_production_wages() + self.dm.total_packaging_wages() + self.dm.total_porter_wages():,.0f}'),
        ]
        for lbl, val in labels:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=lbl, font_size=font_sz(11),
                                  color=TEXT_GRAY, size_hint_y=0.3))
            box.add_widget(Label(text=val, font_size=font_sz(14),
                                  color=PRIMARY, bold=True, size_hint_y=0.7))
            stats_grid.add_widget(box)
        stats.add_widget(stats_grid)
        content.add_widget(stats)

        content.add_widget(SubHeader(text='功能模块'))

        # 功能菜单网格
        menu_items = [
            ('🔧', '生产管理', 'production'),
            ('💰', '费用管理', 'costs'),
            ('👷', '工资管理', 'wages'),
            ('📦', '包装设置', 'packaging'),
            ('📋', '原材料库', 'materials'),
            ('📝', '产品配方', 'products'),
            ('🧮', '最终计算', 'final_calc'),
            ('📊', '数据分析', 'analysis'),
        ]
        menu_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None,
                                height=dp(len(menu_items) // 2 * 90 + 90))
        for icon, name, target in menu_items:
            btn = Button(
                text=f'{icon}\n{name}',
                font_size=font_sz(13),
                background_normal='',
                background_color=(0.98, 0.98, 0.99, 1),
                color=TEXT_DARK,
                size_hint_y=None, height=dp(80))
            btn.bind(on_release=lambda x, t=target: (
                setattr(self.manager, 'current', t),
                getattr(self.manager.get_screen(t), 'on_enter')()
            ))
            menu_grid.add_widget(btn)
        content.add_widget(menu_grid)

        # 版本信息
        content.add_widget(Label(
            text='V2.4 Kivy版 | 未经许可禁止分发',
            font_size=font_sz(11), color=TEXT_GRAY,
            size_hint_y=None, height=dp(30)))
        self.add_widget(scroll)


# ======================== 生产管理 ========================
class ProductionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ref_inputs = {}

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()

        # 顶部导航
        content.add_widget(self.make_back_header('生产管理'))

        # ===== 月产能设置 =====
        card = CardBox(size_hint_y=None, height=dp(100))
        card.add_widget(SectionTitle(text='月产能设置'))
        cap = self.dm.data['capacity']
        cap_box = BoxLayout(orientation='horizontal', spacing=dp(8),
                            size_hint_y=None, height=dp(40))
        cap_box.add_widget(Label(text='月产能(kg):', font_size=font_sz(14),
                                  color=TEXT_DARK, size_hint_x=0.4))
        self.cap_input = TextInput(
            text=str(int(cap.get('月产能_kg', 0))),
            font_size=font_sz(14), input_filter='int',
            multiline=False, size_hint_x=0.6)
        cap_box.add_widget(self.cap_input)
        card.add_widget(cap_box)

        btn_row = BoxLayout(orientation='horizontal', spacing=dp(8),
                            size_hint_y=None, height=dp(36))
        save_btn = Button(text='保存产能', background_normal='',
                          background_color=PRIMARY, color=(1, 1, 1, 1))
        save_btn.bind(on_release=self._save_capacity)
        btn_row.add_widget(save_btn)

        # 联算按钮
        recalc_btn = Button(text='联算工资', background_normal='',
                            background_color=SECONDARY, color=(1, 1, 1, 1))
        recalc_btn.bind(on_release=self._recalc_wages)
        btn_row.add_widget(recalc_btn)
        card.add_widget(btn_row)
        content.add_widget(card)

        # ===== 基本生产效率 =====
        card2 = CardBox(size_hint_y=None, height=dp(280))
        card2.add_widget(SectionTitle(text='基本生产效率'))
        pe = self.dm.data['production_efficiency']

        # 工作时间和天数
        wt_box = BoxLayout(orientation='horizontal', spacing=dp(4),
                           size_hint_y=None, height=dp(36))
        wt_box.add_widget(Label(text='工时/天:', font_size=font_sz(12),
                                 color=TEXT_DARK, size_hint_x=0.25))
        self.hours_input = TextInput(text=str(int(pe.get('工作时间', 8))),
                                      font_size=font_sz(14),
                                      input_filter='float', multiline=False,
                                      size_hint_x=0.2)
        wt_box.add_widget(self.hours_input)
        wt_box.add_widget(Label(text='天数/月:', font_size=font_sz(12),
                                 color=TEXT_DARK, size_hint_x=0.25))
        self.days_input = TextInput(text=str(int(pe.get('天数', 22))),
                                     font_size=font_sz(14),
                                     input_filter='int', multiline=False,
                                     size_hint_x=0.2)
        wt_box.add_widget(self.days_input)
        card2.add_widget(wt_box)

        # 模式选择
        mode_box = BoxLayout(orientation='horizontal', spacing=dp(4),
                             size_hint_y=None, height=dp(36))
        mode_box.add_widget(Label(text='模式:', font_size=font_sz(12),
                                   color=TEXT_DARK, size_hint_x=0.25))
        self.mode_spinner = Spinner(
            text=pe.get('source', 'manual'),
            values=['manual', 'reference'],
            font_size=font_sz(14), size_hint_x=0.7)
        self.mode_spinner.bind(text=self._on_mode_change)
        mode_box.add_widget(self.mode_spinner)
        card2.add_widget(mode_box)

        # A模式: 手动输入
        self.manual_box = BoxLayout(orientation='horizontal', spacing=dp(4),
                                     size_hint_y=None, height=dp(36))
        self.manual_box.add_widget(Label(text='产量/小时(kg):',
                                          font_size=font_sz(12),
                                          color=TEXT_DARK, size_hint_x=0.4))
        self.pe_input = TextInput(
            text=f"{pe.get('产量_每小时_kg', 0):.2f}",
            font_size=font_sz(14), input_filter='float',
            multiline=False, size_hint_x=0.4)
        self.manual_box.add_widget(self.pe_input)
        pe_btn = Button(text='保存', size_hint_x=0.2,
                        background_normal='', background_color=PRIMARY,
                        color=(1, 1, 1, 1), font_size=font_sz(12))
        pe_btn.bind(on_release=self._save_pe_manual)
        self.manual_box.add_widget(pe_btn)
        card2.add_widget(self.manual_box)

        # B模式: 参考项目
        ref_content = BoxLayout(orientation='vertical', spacing=dp(4),
                                 size_hint_y=None, height=dp(150))
        ref_content.add_widget(Label(text='添加参考项目:',
                                      font_size=font_sz(12), color=TEXT_GRAY,
                                      size_hint_y=None, height=dp(20)))
        ref_row = BoxLayout(orientation='horizontal', spacing=dp(4),
                             size_hint_y=None, height=dp(32))
        self.ref_name_input = TextInput(hint_text='名称',
                                         font_size=font_sz(12),
                                         multiline=False, size_hint_x=0.3)
        ref_row.add_widget(self.ref_name_input)
        self.ref_output_input = TextInput(hint_text='产量(kg)',
                                           font_size=font_sz(12),
                                           input_filter='float',
                                           multiline=False, size_hint_x=0.25)
        ref_row.add_widget(self.ref_output_input)
        self.ref_hours_input = TextInput(hint_text='工时(时)',
                                          font_size=font_sz(12),
                                          input_filter='float',
                                          multiline=False, size_hint_x=0.2)
        ref_row.add_widget(self.ref_hours_input)
        ref_add_btn = Button(text='+', size_hint_x=0.15,
                             background_normal='', background_color=SECONDARY,
                             color=(1, 1, 1, 1), font_size=font_sz(16))
        ref_add_btn.bind(on_release=self._add_ref_project)
        ref_row.add_widget(ref_add_btn)
        ref_content.add_widget(ref_row)

        # 参考项目列表
        self.ref_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.ref_list.bind(minimum_height=self.ref_list.setter('height'))
        ref_scroll = ScrollView(size_hint_y=None, height=dp(100))
        ref_scroll.add_widget(self.ref_list)
        ref_content.add_widget(ref_scroll)

        card2.add_widget(ref_content)

        # 当前效率显示
        eff_kg = pe.get('产量_每小时_kg', 0)
        card2.add_widget(InfoRow('当前产量/小时(kg):', f'{eff_kg:.2f}'))
        monthly = eff_kg * pe.get('工作时间', 8) * pe.get('天数', 22)
        card2.add_widget(InfoRow('月产能(效率计算):', f'{monthly:,.1f} kg'))

        content.add_widget(card2)

        self._update_mode_visibility()
        self._refresh_ref_projects()
        self.add_widget(scroll)

    def _save_capacity(self, *args):
        try:
            val = int(self.cap_input.text)
            self.dm.update_capacity('kg', val)
            self.show_popup('提示', f'产能已更新为 {val:,} kg')
        except ValueError:
            self.show_popup('错误', '请输入有效数字')

    def _recalc_wages(self, *args):
        try:
            self.dm.calc_porter_wages()
            self.dm.calc_production_wages()
            self.dm.calc_packaging_wages()
            self.show_popup('提示', '所有工资已联算更新')
        except Exception as e:
            self.show_popup('错误', f'联算失败: {str(e)}')

    def _on_mode_change(self, spinner, text):
        self._update_mode_visibility()
        if text == 'reference':
            self.dm.update_pe_source('reference')
            self.dm._update_ref_avg()
            self.dm.save()
        else:
            self.dm.update_pe_source('manual')
        self._refresh_display()

    def _update_mode_visibility(self):
        is_manual = self.mode_spinner.text == 'manual'
        self.manual_box.opacity = 1 if is_manual else 0.3
        self.manual_box.disabled = not is_manual
        for child in self.ref_list.children:
            child.opacity = 0.3 if is_manual else 1
            child.disabled = is_manual

    def _save_pe_manual(self, *args):
        try:
            val = float(self.pe_input.text)
            self.dm.update_pe_manual(val)
            self.show_popup('提示', f'已设置产量/小时为 {val:.2f} kg')
        except ValueError:
            self.show_popup('错误', '请输入有效数字')

    def _add_ref_project(self, *args):
        name = self.ref_name_input.text.strip()
        try:
            output = float(self.ref_output_input.text)
            hours = float(self.ref_hours_input.text)
        except ValueError:
            self.show_popup('错误', '请输入有效数字')
            return
        if not name:
            self.show_popup('错误', '请输入项目名称')
            return
        self.dm.add_ref_project(name, output, hours)
        self.ref_name_input.text = ''
        self.ref_output_input.text = ''
        self.ref_hours_input.text = ''
        self._refresh_ref_projects()
        self._refresh_display()

    def _delete_ref_project(self, name):
        self.dm.delete_ref_project(name)
        self._refresh_ref_projects()
        self._refresh_display()

    def _refresh_ref_projects(self):
        self.ref_list.clear_widgets()
        pe = self.dm.data.get('production_efficiency', {})
        refs = pe.get('ref_projects', [])
        for ref in refs:
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(28), spacing=dp(4))
            eff = ref['output_kg'] / ref['hours'] if ref['hours'] > 0 else 0
            row.add_widget(Label(text=f"{ref['name']}: {ref['output_kg']:.0f}kg/{ref['hours']:.1f}h={eff:.1f}kg/h",
                                  font_size=font_sz(11), color=TEXT_DARK,
                                  size_hint_x=0.8, halign='left',
                                  text_size=(dp(200), None)))
            del_btn = Button(text='✕', size_hint_x=0.15,
                             background_normal='', background_color=DANGER,
                             color=(1, 1, 1, 1), font_size=font_sz(12))
            del_btn.bind(on_release=lambda x, n=ref['name']: self._delete_ref_project(n))
            row.add_widget(del_btn)
            self.ref_list.add_widget(row)

    def _refresh_display(self):
        pe = self.dm.data['production_efficiency']
        eff_kg = pe.get('产量_每小时_kg', 0)
        self.pe_input.text = f'{eff_kg:.2f}'
        # 刷新当前页面
        Clock.schedule_once(lambda dt: self.on_enter(), 0.1)


# ======================== 费用管理 ========================
class CostsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()
        content.add_widget(self.make_back_header('费用管理'))

        # ===== 固定费用 =====
        card = CardBox(size_hint_y=None, height=dp(200))
        card.add_widget(SectionTitle(text=f'固定费用 (¥{self.dm.total_fixed_costs():,.0f})'))
        self._build_fixed_list(card)
        add_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(36), spacing=dp(4))
        self.fc_name = TextInput(hint_text='名称', font_size=font_sz(12),
                                  multiline=False, size_hint_x=0.4)
        add_box.add_widget(self.fc_name)
        self.fc_price = TextInput(hint_text='金额', font_size=font_sz(12),
                                   input_filter='float', multiline=False,
                                   size_hint_x=0.3)
        add_box.add_widget(self.fc_price)
        add_btn = Button(text='+ 添加', size_hint_x=0.25,
                         background_normal='', background_color=PRIMARY,
                         color=(1, 1, 1, 1), font_size=font_sz(12))
        add_btn.bind(on_release=self._add_fixed_cost)
        add_box.add_widget(add_btn)
        card.add_widget(add_box)
        content.add_widget(card)

        # ===== 管理员费用 =====
        card2 = CardBox(size_hint_y=None, height=dp(250))
        card2.add_widget(SectionTitle(text=f'管理员费用 (¥{self.dm.total_admin_costs():,.0f})'))
        self._build_admin_list(card2)
        add_box2 = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(36), spacing=dp(4))
        self.ac_name = TextInput(hint_text='名称', font_size=font_sz(12),
                                  multiline=False, size_hint_x=0.3)
        add_box2.add_widget(self.ac_name)
        self.ac_price = TextInput(hint_text='单价', font_size=font_sz(12),
                                   input_filter='float', multiline=False,
                                   size_hint_x=0.2)
        add_box2.add_widget(self.ac_price)
        self.ac_qty = TextInput(hint_text='数量', font_size=font_sz(12),
                                 input_filter='int', multiline=False,
                                 size_hint_x=0.15)
        add_box2.add_widget(self.ac_qty)
        add_btn2 = Button(text='+', size_hint_x=0.15,
                          background_normal='', background_color=PRIMARY,
                          color=(1, 1, 1, 1), font_size=font_sz(16))
        add_btn2.bind(on_release=self._add_admin_cost)
        add_box2.add_widget(add_btn2)
        card2.add_widget(add_box2)
        content.add_widget(card2)

        # ===== 电费 =====
        card3 = CardBox(size_hint_y=None, height=dp(80))
        card3.add_widget(SectionTitle(text='电费设置'))
        elec_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(36), spacing=dp(4))
        elec_row.add_widget(Label(text='单价(元/kg):', font_size=font_sz(12),
                                   color=TEXT_DARK, size_hint_x=0.4))
        self.elec_input = TextInput(
            text=f"{self.dm.data['electricity']['电费单价元_kg']:.4f}",
            font_size=font_sz(14), input_filter='float', multiline=False,
            size_hint_x=0.3)
        elec_row.add_widget(self.elec_input)
        elec_btn = Button(text='保存', size_hint_x=0.2,
                          background_normal='', background_color=SECONDARY,
                          color=(1, 1, 1, 1), font_size=font_sz(12))
        elec_btn.bind(on_release=lambda x: (
            self.dm.update_electricity_price(float(self.elec_input.text)),
            self.show_popup('提示', '电费单价已更新')))
        elec_row.add_widget(elec_btn)
        card3.add_widget(elec_row)
        content.add_widget(card3)

        # 总费用汇总
        total = self.dm.total_fixed_costs() + self.dm.total_admin_costs() + self.dm.calc_electricity()
        card4 = CardBox(size_hint_y=None, height=dp(40))
        card4.add_widget(InfoRow('费用总计:', f'¥{total:,.2f}', value_color=PRIMARY))
        content.add_widget(card4)

        self.add_widget(scroll)

    def _build_fixed_list(self, parent):
        scroll = ScrollView(size_hint_y=None, height=dp(100))
        box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(2))
        box.bind(minimum_height=box.setter('height'))
        for i, fc in enumerate(self.dm.data['fixed_costs']):
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(28), spacing=dp(4))
            row.add_widget(Label(text=f"{fc['name']}: ¥{fc['price']:.0f}",
                                  font_size=font_sz(12), color=TEXT_DARK,
                                  size_hint_x=0.8, halign='left',
                                  text_size=(dp(200), None)))
            del_btn = Button(text='✕', size_hint_x=0.15,
                             background_normal='', background_color=DANGER,
                             color=(1, 1, 1, 1), font_size=font_sz(12))
            del_btn.bind(on_release=lambda x, idx=i: (
                self.dm.delete_fixed_cost(idx), self.on_enter()))
            row.add_widget(del_btn)
            box.add_widget(row)
        scroll.add_widget(box)
        parent.add_widget(scroll)

    def _build_admin_list(self, parent):
        scroll = ScrollView(size_hint_y=None, height=dp(120))
        box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(2))
        box.bind(minimum_height=box.setter('height'))
        for i, ac in enumerate(self.dm.data['admin_costs']):
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(28), spacing=dp(4))
            row.add_widget(Label(
                text=f"{ac['name']}: ¥{ac['price']:.0f}×{ac['qty']}=¥{ac['total']:.0f}",
                font_size=font_sz(11), color=TEXT_DARK, size_hint_x=0.8,
                halign='left', text_size=(dp(200), None)))
            del_btn = Button(text='✕', size_hint_x=0.15,
                             background_normal='', background_color=DANGER,
                             color=(1, 1, 1, 1), font_size=font_sz(12))
            del_btn.bind(on_release=lambda x, idx=i: (
                self.dm.delete_admin_cost(idx), self.on_enter()))
            row.add_widget(del_btn)
            box.add_widget(row)
        scroll.add_widget(box)
        parent.add_widget(scroll)

    def _add_fixed_cost(self, *args):
        name = self.fc_name.text.strip()
        try:
            price = float(self.fc_price.text)
        except ValueError:
            self.show_popup('错误', '请输入有效金额')
            return
        if not name:
            self.show_popup('错误', '请输入名称')
            return
        self.dm.add_fixed_cost(name, price)
        self.fc_name.text = ''
        self.fc_price.text = ''
        self.on_enter()

    def _add_admin_cost(self, *args):
        name = self.ac_name.text.strip()
        try:
            price = float(self.ac_price.text)
            qty = int(self.ac_qty.text)
        except ValueError:
            self.show_popup('错误', '请输入有效数字')
            return
        if not name:
            self.show_popup('错误', '请输入名称')
            return
        self.dm.add_admin_cost(name, price, qty)
        self.ac_name.text = ''
        self.ac_price.text = ''
        self.ac_qty.text = ''
        self.on_enter()


# ======================== 工资管理 ========================
class WagesScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_sub = 'porter'

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()
        content.add_widget(self.make_back_header('工资管理'))

        # 子导航 - 三个工资模块
        tab_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(40), spacing=dp(4))
        tabs = [('搬运工', 'porter'), ('生产线', 'production'), ('包装', 'packaging')]
        for label, key in tabs:
            btn = Button(text=label,
                         background_normal='',
                         background_color=PRIMARY if self.active_sub == key else (0.85, 0.85, 0.85, 1),
                         color=(1, 1, 1, 1) if self.active_sub == key else TEXT_DARK,
                         font_size=font_sz(13))
            btn.bind(on_release=lambda x, k=key: self._switch_tab(k))
            tab_box.add_widget(btn)
        content.add_widget(tab_box)

        if self.active_sub == 'porter':
            self._build_porter(content)
        elif self.active_sub == 'production':
            self._build_production(content)
        else:
            self._build_packaging(content)

        self.add_widget(scroll)

    def _switch_tab(self, key):
        self.active_sub = key
        self.on_enter()

    def _build_porter(self, content):
        cap_kg = self.dm.data['capacity']['月产能_kg']
        content.add_widget(CardBox(size_hint_y=None, height=dp(40)))
        content.children[0].add_widget(
            InfoRow(f'搬运工工资 (产能{cap_kg:,.0f}kg)',
                    f'¥{self.dm.total_porter_wages():,.0f}',
                    value_color=PRIMARY))

        # 添加搬运工
        add_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(36), spacing=dp(4))
        self.p_name = TextInput(hint_text='姓名', font_size=font_sz(12),
                                 multiline=False, size_hint_x=0.35)
        add_box.add_widget(self.p_name)
        self.p_wage = TextInput(hint_text='基本工资', font_size=font_sz(12),
                                 input_filter='float', multiline=False,
                                 size_hint_x=0.35)
        add_box.add_widget(self.p_wage)
        add_btn = Button(text='+', size_hint_x=0.2,
                         background_normal='', background_color=PRIMARY,
                         color=(1, 1, 1, 1), font_size=font_sz(16))
        add_btn.bind(on_release=self._add_porter)
        add_box.add_widget(add_btn)
        content.add_widget(add_box)

        # 列表
        for i, p in enumerate(self.dm.data['porter_wages']):
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(32), spacing=dp(4))
            row.add_widget(Label(
                text=f"{p['name']}: ¥{p['base_wage']:.0f} + {p['correction']:.2f} = ¥{p['actual']:.2f}",
                font_size=font_sz(11), color=TEXT_DARK, halign='left',
                text_size=(dp(220), None)))
            del_btn = Button(text='✕', size_hint_x=0.12,
                             background_normal='', background_color=DANGER,
                             color=(1, 1, 1, 1), font_size=font_sz(12))
            del_btn.bind(on_release=lambda x, idx=i: (
                self.dm.delete_porter(idx), self.on_enter()))
            row.add_widget(del_btn)
            content.add_widget(row)

    def _add_porter(self, *args):
        name = self.p_name.text.strip()
        try:
            wage = float(self.p_wage.text)
        except ValueError:
            self.show_popup('错误', '请输入有效数字')
            return
        if not name:
            self.show_popup('错误', '请输入姓名')
            return
        self.dm.add_porter(name, wage)
        self.p_name.text = ''
        self.p_wage.text = ''
        self.on_enter()

    def _build_production(self, content):
        content.add_widget(CardBox(size_hint_y=None, height=dp(40)))
        total = self.dm.total_production_wages()
        content.children[0].add_widget(
            InfoRow('生产线工资总计:', f'¥{total:,.0f}', value_color=PRIMARY))

        # 添加工人
        add_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(36), spacing=dp(2))
        self.pw_name = TextInput(hint_text='姓名', font_size=font_sz(11),
                                  multiline=False, size_hint_x=0.25)
        add_box.add_widget(self.pw_name)
        self.pw_wage = TextInput(hint_text='基本工资', font_size=font_sz(11),
                                  input_filter='float', multiline=False,
                                  size_hint_x=0.2)
        add_box.add_widget(self.pw_wage)
        self.pw_rate = TextInput(hint_text='额外元/时', font_size=font_sz(11),
                                  input_filter='float', multiline=False,
                                  size_hint_x=0.2)
        add_box.add_widget(self.pw_rate)
        self.pw_bonus = TextInput(hint_text='满勤', font_size=font_sz(11),
                                   input_filter='float', multiline=False,
                                   size_hint_x=0.15)
        add_box.add_widget(self.pw_bonus)
        add_btn = Button(text='+', size_hint_x=0.12,
                         background_normal='', background_color=PRIMARY,
                         color=(1, 1, 1, 1), font_size=font_sz(16))
        add_btn.bind(on_release=self._add_production)
        add_box.add_widget(add_btn)
        content.add_widget(add_box)

        # 列表
        for i, w in enumerate(self.dm.data['production_wages']):
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(28), spacing=dp(2))
            row.add_widget(Label(
                text=f"{w['name']}: {w['actual_hours']:.1f}h × ¥{w['extra_rate']:.0f} + ¥{w['bonus']:.0f} = ¥{w['total']:.0f}",
                font_size=font_sz(10), color=TEXT_DARK, halign='left',
                text_size=(dp(220), None)))
            del_btn = Button(text='✕', size_hint_x=0.1,
                             background_normal='', background_color=DANGER,
                             color=(1, 1, 1, 1), font_size=font_sz(12))
            del_btn.bind(on_release=lambda x, idx=i: (
                self.dm.delete_production_worker(idx), self.on_enter()))
            row.add_widget(del_btn)
            content.add_widget(row)

    def _add_production(self, *args):
        name = self.pw_name.text.strip()
        try:
            wage = float(self.pw_wage.text)
            rate = float(self.pw_rate.text)
            bonus = float(self.pw_bonus.text)
        except ValueError:
            self.show_popup('错误', '请输入有效数字')
            return
        if not name:
            self.show_popup('错误', '请输入姓名')
            return
        self.dm.add_production_worker(name, wage, rate, bonus)
        for f in [self.pw_name, self.pw_wage, self.pw_rate, self.pw_bonus]:
            f.text = ''
        self.on_enter()

    def _build_packaging(self, content):
        content.add_widget(CardBox(size_hint_y=None, height=dp(40)))
        total = self.dm.total_packaging_wages()
        content.children[0].add_widget(
            InfoRow('包装工资总计:', f'¥{total:,.0f}', value_color=PRIMARY))

        add_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(36), spacing=dp(2))
        self.pk_name = TextInput(hint_text='姓名', font_size=font_sz(11),
                                  multiline=False, size_hint_x=0.25)
        add_box.add_widget(self.pk_name)
        self.pk_wage = TextInput(hint_text='基本工资', font_size=font_sz(11),
                                  input_filter='float', multiline=False,
                                  size_hint_x=0.2)
        add_box.add_widget(self.pk_wage)
        self.pk_sub = TextInput(hint_text='职位补贴', font_size=font_sz(11),
                                 input_filter='float', multiline=False,
                                 size_hint_x=0.2)
        add_box.add_widget(self.pk_sub)
        self.pk_bonus = TextInput(hint_text='满勤', font_size=font_sz(11),
                                   input_filter='float', multiline=False,
                                   size_hint_x=0.15)
        add_box.add_widget(self.pk_bonus)
        add_btn = Button(text='+', size_hint_x=0.12,
                         background_normal='', background_color=PRIMARY,
                         color=(1, 1, 1, 1), font_size=font_sz(16))
        add_btn.bind(on_release=self._add_packaging)
        add_box.add_widget(add_btn)
        content.add_widget(add_box)

        for i, w in enumerate(self.dm.data['packaging_wages']):
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(28), spacing=dp(2))
            row.add_widget(Label(
                text=f"{w['name']}: ¥{w['base_wage']:.0f}+¥{w['subsidy']:.0f}=¥{w['final']:.0f}",
                font_size=font_sz(10), color=TEXT_DARK, halign='left',
                text_size=(dp(220), None)))
            del_btn = Button(text='✕', size_hint_x=0.1,
                             background_normal='', background_color=DANGER,
                             color=(1, 1, 1, 1), font_size=font_sz(12))
            del_btn.bind(on_release=lambda x, idx=i: (
                self.dm.delete_packaging_worker(idx), self.on_enter()))
            row.add_widget(del_btn)
            content.add_widget(row)

    def _add_packaging(self, *args):
        name = self.pk_name.text.strip()
        try:
            wage = float(self.pk_wage.text)
            sub = float(self.pk_sub.text)
            bonus = float(self.pk_bonus.text)
        except ValueError:
            self.show_popup('错误', '请输入有效数字')
            return
        if not name:
            self.show_popup('错误', '请输入姓名')
            return
        self.dm.add_packaging_worker(name, wage, sub, bonus)
        for f in [self.pk_name, self.pk_wage, self.pk_sub, self.pk_bonus]:
            f.text = ''
        self.on_enter()


# ======================== 包装设置 ========================
class PackagingScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()
        content.add_widget(self.make_back_header('包装设置'))

        # 包装系数
        card = CardBox(size_hint_y=None, height=dp(140))
        card.add_widget(SectionTitle(text='包装系数'))
        pc = self.dm.data['packaging_coefficient']
        values = list(pc.values()) if isinstance(pc, dict) else [0, 0, 0]
        last_wage = values[0] if len(values) > 0 else 0
        last_output = values[1] if len(values) > 1 else 0
        coeff = values[2] if len(values) > 2 else 0

        card.add_widget(self.make_input_row(
            '上月包装工资:', TextInput(text=f'{last_wage:.0f}',
                                    font_size=font_sz(14),
                                    input_filter='float', multiline=False)))
        card.add_widget(self.make_input_row(
            '上月总产量(kg):', TextInput(text=f'{last_output:.0f}',
                                        font_size=font_sz(14),
                                        input_filter='float', multiline=False)))
        card.add_widget(InfoRow('当前包装系数:', f'{coeff:.6f}', value_color=SECONDARY))
        content.add_widget(card)

        # 包装费用
        card2 = CardBox(size_hint_y=None, height=dp(120))
        card2.add_widget(SectionTitle(text='包装费用'))
        pc_data = self.dm.data['product_costs']
        film_input = TextInput(text=f"{pc_data.get('包装膜费用', 0):.2f}",
                                font_size=font_sz(14), input_filter='float',
                                multiline=False)
        card2.add_widget(self.make_input_row('包装膜费用:', film_input))
        carton_input = TextInput(text=f"{pc_data.get('纸箱费用', 0):.2f}",
                                  font_size=font_sz(14), input_filter='float',
                                  multiline=False)
        card2.add_widget(self.make_input_row('纸箱费用:', carton_input))
        save_btn = Button(text='保存包装费用', size_hint_y=None, height=dp(36),
                          background_normal='', background_color=PRIMARY,
                          color=(1, 1, 1, 1))
        save_btn.bind(on_release=lambda x: (
            self.dm.update_product_costs(
                float(film_input.text), float(carton_input.text)),
            self.show_popup('提示', '包装费用已更新')))
        card2.add_widget(save_btn)
        content.add_widget(card2)

        # 包装人员汇总
        card3 = CardBox(size_hint_y=None, height=dp(40))
        total_pkg = self.dm.total_packaging_wages()
        card3.add_widget(InfoRow('包装人员工资总计:', f'¥{total_pkg:,.0f}',
                                  value_color=PRIMARY))
        content.add_widget(card3)

        self.add_widget(scroll)


# ======================== 原材料库 ========================
class MaterialsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()
        content.add_widget(self.make_back_header('原材料库'))

        # 添加原材料
        add_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(40), spacing=dp(4))
        self.mat_name = TextInput(hint_text='原材料名称', font_size=font_sz(12),
                                   multiline=False, size_hint_x=0.4)
        add_box.add_widget(self.mat_name)
        self.mat_price = TextInput(hint_text='元/kg', font_size=font_sz(12),
                                    input_filter='float', multiline=False,
                                    size_hint_x=0.3)
        add_box.add_widget(self.mat_price)
        add_btn = Button(text='+ 添加', size_hint_x=0.25,
                         background_normal='', background_color=PRIMARY,
                         color=(1, 1, 1, 1), font_size=font_sz(12))
        add_btn.bind(on_release=self._add_material)
        add_box.add_widget(add_btn)
        content.add_widget(add_box)

        # 原材料列表
        for i, mat in enumerate(self.dm.data['raw_materials']):
            card = CardBox(size_hint_y=None, height=dp(50))
            row = BoxLayout(orientation='horizontal', spacing=dp(4),
                            size_hint_y=None, height=dp(30))
            row.add_widget(Label(text=mat['name'], font_size=font_sz(14),
                                  color=TEXT_DARK, bold=True,
                                  size_hint_x=0.35, halign='left',
                                  text_size=(dp(100), None)))
            row.add_widget(Label(text=f"¥{mat['price_kg']:.4f}/kg",
                                  font_size=font_sz(13), color=PRIMARY,
                                  size_hint_x=0.35))
            del_btn = Button(text='✕', size_hint_x=0.2,
                             background_normal='', background_color=DANGER,
                             color=(1, 1, 1, 1), font_size=font_sz(14))
            del_btn.bind(on_release=lambda x, idx=i: (
                self.dm.delete_material(idx), self.on_enter()))
            row.add_widget(del_btn)
            card.add_widget(row)
            content.add_widget(card)

        content.add_widget(Label(
            text=f'共 {len(self.dm.data["raw_materials"])} 种原材料',
            font_size=font_sz(12), color=TEXT_GRAY,
            size_hint_y=None, height=dp(30)))
        self.add_widget(scroll)

    def _add_material(self, *args):
        name = self.mat_name.text.strip()
        try:
            price = float(self.mat_price.text)
        except ValueError:
            self.show_popup('错误', '请输入有效价格')
            return
        if not name:
            self.show_popup('错误', '请输入原材料名称')
            return
        # 检查重复
        if name in self.dm.get_material_names():
            self.show_popup('提示', f'原材料"{name}"已存在')
            return
        self.dm.add_material(name, price)
        self.mat_name.text = ''
        self.mat_price.text = ''
        self.on_enter()


# ======================== 产品配方 ========================
class ProductsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_product = None

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()
        content.add_widget(self.make_back_header('产品配方'))

        # 添加产品
        add_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(40), spacing=dp(4))
        self.prod_name = TextInput(hint_text='产品名称', font_size=font_sz(12),
                                    multiline=False, size_hint_x=0.6)
        add_box.add_widget(self.prod_name)
        add_btn = Button(text='+ 添加', size_hint_x=0.35,
                         background_normal='', background_color=PRIMARY,
                         color=(1, 1, 1, 1), font_size=font_sz(12))
        add_btn.bind(on_release=self._add_product)
        add_box.add_widget(add_btn)
        content.add_widget(add_box)

        # 产品列表
        for i, prod in enumerate(self.dm.data['products']):
            btn = Button(
                text=f"{prod['name']} ({len(prod.get('ingredients', []))}种原料)",
                font_size=font_sz(13), color=TEXT_DARK,
                background_normal='',
                background_color=(0.95, 0.95, 0.97, 1) if self.selected_product == i else (0.98, 0.98, 0.99, 1),
                size_hint_y=None, height=dp(40))
            btn.bind(on_release=lambda x, idx=i: self._select_product(idx))
            content.add_widget(btn)

        # 选中产品的配方详情
        if self.selected_product is not None and self.selected_product < len(self.dm.data['products']):
            prod = self.dm.data['products'][self.selected_product]
            card = CardBox(size_hint_y=None, height=dp(300))
            card.add_widget(SectionTitle(text=f"配方: {prod['name']}"))

            # 投料产出比
            ratio_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                                  height=dp(36), spacing=dp(4))
            ratio_box.add_widget(Label(text='投料(kg):', font_size=font_sz(12),
                                        color=TEXT_DARK, size_hint_x=0.3))
            input_input = TextInput(text=f"{prod.get('input_kg', 0):.2f}",
                                     font_size=font_sz(14),
                                     input_filter='float', multiline=False,
                                     size_hint_x=0.3)
            ratio_box.add_widget(input_input)
            ratio_box.add_widget(Label(text='产出(kg):', font_size=font_sz(12),
                                        color=TEXT_DARK, size_hint_x=0.3))
            output_input = TextInput(text=f"{prod.get('output_kg', 0):.2f}",
                                      font_size=font_sz(14),
                                      input_filter='float', multiline=False,
                                      size_hint_x=0.3)
            ratio_box.add_widget(output_input)
            ratio_save = Button(text='✓', size_hint_x=0.1,
                                background_normal='', background_color=SECONDARY,
                                color=(1, 1, 1, 1), font_size=font_sz(16))
            ratio_save.bind(on_release=lambda x: (
                self.dm.update_product_ratio(
                    self.selected_product,
                    float(input_input.text),
                    float(output_input.text)),
                self.show_popup('提示', '投料产出比已更新'),
                self.on_enter()))
            ratio_box.add_widget(ratio_save)
            card.add_widget(ratio_box)

            # 配方配料
            card.add_widget(SubHeader(text='配料列表:'))
            for j, ing in enumerate(prod.get('ingredients', [])):
                row = BoxLayout(orientation='horizontal', size_hint_y=None,
                                height=dp(28), spacing=dp(4))
                row.add_widget(Label(
                    text=f"{ing['material_name']}: {ing['usage_kg']:.2f}kg",
                    font_size=font_sz(11), color=TEXT_DARK,
                    halign='left', text_size=(dp(180), None)))
                del_btn = Button(text='✕', size_hint_x=0.15,
                                 background_normal='', background_color=DANGER,
                                 color=(1, 1, 1, 1), font_size=font_sz(12))
                del_btn.bind(on_release=lambda x, idx=j: (
                    self.dm.delete_ingredient(self.selected_product, idx),
                    self.on_enter()))
                row.add_widget(del_btn)
                card.add_widget(row)

            # 添加配料
            if self.dm.get_material_names():
                ing_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                                    height=dp(36), spacing=dp(4))
                ing_spinner = Spinner(text='选择原料',
                                       values=self.dm.get_material_names(),
                                       font_size=font_sz(12),
                                       size_hint_x=0.4)
                ing_box.add_widget(ing_spinner)
                ing_input = TextInput(hint_text='用量(kg)',
                                       font_size=font_sz(12),
                                       input_filter='float', multiline=False,
                                       size_hint_x=0.3)
                ing_box.add_widget(ing_input)
                ing_add = Button(text='+', size_hint_x=0.15,
                                 background_normal='', background_color=PRIMARY,
                                 color=(1, 1, 1, 1), font_size=font_sz(16))
                ing_add.bind(on_release=lambda x: (
                    self.dm.add_ingredient(
                        self.selected_product,
                        ing_spinner.text,
                        float(ing_input.text)),
                    self.on_enter()))
                ing_box.add_widget(ing_add)
                card.add_widget(ing_box)

            # 原材料成本计算
            raw_cost = self.dm.calc_product_raw_cost(self.selected_product)
            card.add_widget(InfoRow('原材料成本:', f'¥{raw_cost:.4f}/kg',
                                     value_color=SECONDARY))
            content.add_widget(card)

        self.add_widget(scroll)

    def _add_product(self, *args):
        name = self.prod_name.text.strip()
        if not name:
            self.show_popup('错误', '请输入产品名称')
            return
        self.dm.add_product(name)
        self.prod_name.text = ''
        self.selected_product = len(self.dm.data['products']) - 1
        self.on_enter()

    def _select_product(self, idx):
        self.selected_product = idx
        self.on_enter()


# ======================== 最终计算 ========================
class FinalCalcScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()
        content.add_widget(self.make_back_header('最终计算'))

        cap_kg = self.dm.data['capacity']['月产能_kg']
        if cap_kg == 0:
            content.add_widget(Label(
                text='请先在"生产管理"中设置月产能',
                font_size=font_sz(14), color=DANGER,
                size_hint_y=None, height=dp(60)))
            self.add_widget(scroll)
            return

        total_cost = self.dm.total_costs()
        costs_per_kg = total_cost / cap_kg

        # 成本汇总
        card = CardBox(size_hint_y=None, height=dp(220))
        card.add_widget(SectionTitle(text=f'成本汇总 (产能: {cap_kg:,.0f} kg)'))

        items = [
            ('固定费用', self.dm.total_fixed_costs()),
            ('管理员费用', self.dm.total_admin_costs()),
            ('电费', self.dm.calc_electricity()),
            ('搬运工工资', self.dm.total_porter_wages()),
            ('生产线工资', self.dm.total_production_wages()),
            ('包装人员工资', self.dm.total_packaging_wages()),
        ]
        for label, val in items:
            card.add_widget(InfoRow(label, f'¥{val:,.2f}', TEXT_GRAY))
        card.add_widget(InfoRow('总费用', f'¥{total_cost:,.2f}', PRIMARY))
        card.add_widget(InfoRow('每kg均摊', f'¥{costs_per_kg:.4f}', PRIMARY))
        content.add_widget(card)

        # 各产品成本
        card2 = CardBox(size_hint_y=None)
        card2.add_widget(SectionTitle(text='各产品成本'))

        pc_data = self.dm.data['product_costs']
        film = pc_data.get('包装膜费用', 0)
        carton = pc_data.get('纸箱费用', 0)

        for i, prod in enumerate(self.dm.data.get('products', [])):
            raw_cost = self.dm.calc_product_raw_cost(i)
            final = self.dm.calc_final_cost(raw_cost)
            ratio = prod.get('output_kg', 0) / prod.get('input_kg', 0) if prod.get('input_kg', 0) > 0 else 1
            final_adj = final / ratio if ratio > 0 else final

            detail = BoxLayout(orientation='vertical', size_hint_y=None)
            detail.bind(minimum_height=detail.setter('height'))
            detail.add_widget(Label(
                text=f"{prod['name']} (投料{prod.get('input_kg', 0):.0f}→产出{prod.get('output_kg', 0):.0f}kg)",
                font_size=font_sz(13), color=TEXT_DARK, bold=True,
                size_hint_y=None, height=dp(24), halign='left',
                text_size=(dp(260), None)))
            detail.add_widget(InfoRow('  原材料成本:', f'¥{raw_cost:.4f}/kg'))
            detail.add_widget(InfoRow('  均摊费用:', f'¥{costs_per_kg:.4f}/kg'))
            detail.add_widget(InfoRow('  包装膜:', f'¥{film:.2f}/kg'))
            detail.add_widget(InfoRow('  纸箱:', f'¥{carton:.2f}/kg'))
            detail.add_widget(InfoRow(f'  成品成本:', f'¥{final_adj:.4f}/件',
                                      value_color=SECONDARY))
            card2.add_widget(detail)
            card2.height = dp(50 + (len(prod.get('ingredients', [])) * 28) + 120)

        content.add_widget(card2)

        self.add_widget(scroll)


# ======================== 数据分析 ========================
class AnalysisScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        scroll, content = self.make_scroll_content()
        content.add_widget(self.make_back_header('数据分析'))

        cap_kg = self.dm.data['capacity']['月产能_kg']
        if cap_kg == 0:
            content.add_widget(Label(
                text='请先在"生产管理"中设置月产能',
                font_size=font_sz(14), color=DANGER,
                size_hint_y=None, height=dp(60)))
            self.add_widget(scroll)
            return

        # 产能-成本分析
        card = CardBox(size_hint_y=None, height=dp(300))
        card.add_widget(SectionTitle(text='产能-成本分析'))

        cap_range = [cap_kg * 0.5, cap_kg * 0.75, cap_kg, cap_kg * 1.25, cap_kg * 1.5]
        card.add_widget(SubHeader(text='不同产能下的总费用:'))
        for c in cap_range:
            tc = self.dm.total_costs_at_capacity(c)
            card.add_widget(InfoRow(f'{c:,.0f} kg', f'¥{tc:,.0f}'))
        content.add_widget(card)

        # 成本占比
        card2 = CardBox(size_hint_y=None, height=dp(220))
        card2.add_widget(SectionTitle(text='成本占比分析'))
        items = [
            ('固定费用', self.dm.total_fixed_costs()),
            ('管理员费用', self.dm.total_admin_costs()),
            ('电费', self.dm.calc_electricity()),
            ('搬运工工资', self.dm.total_porter_wages()),
            ('生产线工资', self.dm.total_production_wages()),
            ('包装人员工资', self.dm.total_packaging_wages()),
        ]
        total = sum(v for _, v in items)
        if total > 0:
            for label, val in items:
                pct = val / total * 100
                card2.add_widget(InfoRow(label, f'¥{val:,.0f} ({pct:.1f}%)'))
        content.add_widget(card2)

        # 敏感性分析
        if self.dm.get_material_names():
            card3 = CardBox(size_hint_y=None, height=dp(180))
            card3.add_widget(SectionTitle(text='原材料敏感性分析'))
            mat_spinner = Spinner(text=self.dm.get_material_names()[0],
                                   values=self.dm.get_material_names(),
                                   font_size=font_sz(12), size_hint_y=None,
                                   height=dp(32))
            card3.add_widget(mat_spinner)
            cols = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(36), spacing=dp(4))
            cols.add_widget(Label(text='步长(元):', font_size=font_sz(12),
                                   color=TEXT_DARK, size_hint_x=0.35))
            step_input = TextInput(text='1', font_size=font_sz(14),
                                    input_filter='float', multiline=False,
                                    size_hint_x=0.25)
            cols.add_widget(step_input)
            cols.add_widget(Label(text='次数:', font_size=font_sz(12),
                                   color=TEXT_DARK, size_hint_x=0.2))
            count_input = TextInput(text='5', font_size=font_sz(14),
                                     input_filter='int', multiline=False,
                                     size_hint_x=0.15)
            cols.add_widget(count_input)
            card3.add_widget(cols)
            calc_btn = Button(text='计算敏感性', size_hint_y=None, height=dp(36),
                              background_normal='', background_color=PRIMARY,
                              color=(1, 1, 1, 1))
            calc_btn.bind(on_release=lambda x: self._calc_sensitivity(
                mat_spinner.text, float(step_input.text), int(count_input.text)))
            card3.add_widget(calc_btn)
            content.add_widget(card3)

        self.add_widget(scroll)

    def _calc_sensitivity(self, mat_name, step, count):
        results = self.dm.calc_sensitivity(mat_name, step, count)
        if not results:
            self.show_popup('错误', '无法计算敏感性分析')
            return
        msg = f'原材料"{mat_name}"敏感性分析:\n'
        for r in results[:5]:  # 展示前5个
            msg += f"  ¥{r['price']:.2f}/kg → ¥{r['total_cost']:,.0f}\n"
        self.show_popup('敏感性分析', msg)


# ======================== 启动入口 ========================
if __name__ == '__main__':
    CostApp().run()
