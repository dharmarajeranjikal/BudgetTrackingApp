from Data_Plotter import Excel
from App_Setup import First_Setup, Regular_Check
import os
from datetime import date

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.uix.datatables import MDDataTable
from kivy.lang import Builder
from kivy.metrics import dp


Builder.load_file('frontend.kv')

today = date.today()
month = today.strftime("%B")

XL = Excel()
RC = Regular_Check()

previous_data = int()
manage_constant = ''
constantlist = ['Dummy1']

class LoadingScreen(Screen):

    def startup(self):
        Workbook_status = os.path.isfile(XL.filename)

        if Workbook_status == False:
            # print('Setup loop')
            setup = First_Setup()
            setup.setup()
            self.manager.current = 'prev_data'

        else:
            # print('RC loop')
            RC.check()
            self.manager.current = 'home_screen'

class PrevData(Screen):
    def add_prev_data(self):
        setup = First_Setup()
        prev_data = self.manager.current_screen.ids.prev_data.text
        try:
            setup.previous_data(previous_amount= int(prev_data))
            self.manager.current = 'loading_screen'

        except:
            self.ids.prev_data_label.text = 'Enter a data containing numbers'

class HomeScreen(Screen):
    def on_enter(self, *args):
        total = XL.read_total(month)
        self.ids.expenses_for_this_month.text = str(total)

        prev_total = XL.read_previous(month)
        self.ids.expenses_for_previous_month.text = str(prev_total)

        percentage =XL.percent_saving(int(total), int(prev_total))
        self.ids.percentage.text= percentage

    def feed_data(self):
        particular = self.manager.current_screen.ids.particular.text
        try:
            amount = self.manager.current_screen.ids.amount.text
            amount = int(amount)
            month = today.strftime("%B")
            XL.add_data(base_sheet= month, particular=particular, amount= amount)
            self.ids.particular.text = ''
            self.ids.amount.text= ''
            self.on_enter()


        except:
            self.ids.amount.text = 'Enter only numbers'

    def feed_withdrawn(self):
        try:
            amount = self.manager.current_screen.ids.amount.text
            amount = int(amount)
            month = today.strftime("%B")

            XL.add_data(base_sheet=month, withdrawn= amount)
            self.ids.particular.text = ''
            self.ids.amount.text = ''

        except:
            self.ids.amount.text = 'Enter only numbers'

    def openxl(self):
        os.startfile(XL.filename)

    def quit(self):
        quit()

class ConstantScreen(Screen):

    def on_enter(self, *args):
        global constantlist
        read_list = XL.get_paricular_list('Recurring Constant')
        constantlist = read_list
        self.ids.viewarea.clear_widgets()

        # print('read_list', read_list)

        if read_list == []:
            # print('For no entries')
            lbltext = "No Recurring Constants available\n\n" \
                      "Use + to Add new constant expense\n\n" \
                      "Use ||| to manage constant expenses"
            lbl = Label(text=lbltext, font_size=15, color=(0, 0, 0, 1), halign='center')
            self.ids.viewarea.add_widget(lbl)

        else:
            for btnname in read_list:
                btn = Button(text=btnname, size_hint_y=0.1)
                btn.bind(on_release=lambda btn:self.load_constant(btn.text))
                self.ids.viewarea.add_widget(btn)


    def load_constant(self, constant_name):
        global constantlist
        row = 7 + constantlist.index(constant_name)
        indx = 'C'+str(row)
        amount = XL.get_value('Recurring Constant', indx)
        month =today.strftime('%B')
        XL.add_data(base_sheet=month, particular=constant_name, amount=amount)
        self.manager.current = 'home_screen'
        # print(constant_name, indx, amount, month)

    def goback(self):
        self.manager.current='home_screen'
        self.manager.transition.direction='right'

    def addbutton(self):
        self.manager.current='add_constant'
        self.manager.transition.direction='left'

    def managebutton(self):
        self.manager.current='manage_constant'
        self.manager.transition.direction='up'

class AddConstant(Screen):
    def addconstant(self):
        r_particular = self.manager.current_screen.ids.recurring_particular.text
        r_amount = self.manager.current_screen.ids.recurring_amount.text
        try:
            r_amount = int(r_amount)
            XL.add_data('Recurring Constant', r_particular, r_amount)
            self.manager.current = 'constant_screen'

        except:
            self.ids.recurring_amount.text = 'Enter only numbers'
        #
        # print(r_amount)

    def goback(self):
        self.manager.current = 'constant_screen'
        self.manager.transition.direction = 'right'

class ManageConstant(Screen):

    def on_enter(self, *args):
        read_list = XL.get_paricular_list('Recurring Constant')
        self.ids.viewarea.clear_widgets()

        # print('read_list', read_list)

        if read_list == []:
            # print('For no entries')
            lbltext = "No Recurring Constants available\n\n" \
                      "Use + to Add new constant expense\n\n" \
                      "Use ||| to manage constant expenses"
            lbl = Label(text=lbltext, font_size=15, color=(0, 0, 0, 1), halign='center')
            self.ids.viewarea.add_widget(lbl)
            self.entry_val = True

        else:
            for btnname in read_list:
                btn = Button(text=btnname, size_hint_y=0.1)
                btn.bind(on_release=lambda btn: self.load_constant(btn.text))
                self.ids.viewarea.add_widget(btn)

    def load_constant(self, constant_name):
        global manage_constant
        manage_constant = constant_name
        self.manager.current = 'edit_constant'

    def goback(self):
        self.manager.current='constant_screen'
        self.manager.transition.direction='down'

class EditConstant(Screen):
    global manage_constant
    global constantlist

    def on_enter(self, *args):
        self.ids.particular_name.text = f"for {manage_constant}"

    def update(self):
        update_amount = self.manager.current_screen.ids.updated_amount.text
        row = constantlist.index(manage_constant)
        index = 'C'+ str(row + 7)
        # print(index,'updated with', update_amount)
        try:
            XL.update_data(index, update_amount)
            self.manager.current = 'constant_screen'
            self.manager.transition.direction = 'down'

        except:
            self.ids.update_label.text = 'Enter only numbers'

    def remove(self):
        row = 7 + int(constantlist.index(manage_constant))
        XL.remove_data('Recurring Constant', row)
        self.manager.current = 'constant_screen'
        self.manager.transition.direction = 'down'

    def goback(self):
        self.manager.current = 'manage_constant'
        self.manager.transition.direction = 'down'

class ViewData(Screen):
    def on_enter(self, *args):
        sheets = XL.get_sheets()
        self.ids.tableview.clear_widgets()
        self.ids.base_sheet.values = sheets

    def view_table(self, base_sheet):
        # print(base_sheet)
        self.ids.tableview.clear_widgets()

        plist = XL.get_paricular_list(base_sheet)
        alist = XL.get_amount_list(base_sheet)
        final_list=[]
        for x in range(len(plist)):
            final_list.append((plist[x],alist[x]))

        # print(final_list)

        table = MDDataTable(
                    size_hint =(0.95,1),
                    use_pagination=True,
                    column_data = [
                        ('Particular', dp(35)),
                        ('Amount', dp(20))
                    ],
                    row_data=final_list
        )
        self.ids.tableview.add_widget(table)

    def goback(self):
        self.manager.current = 'home_screen'

#Boiler plate code
class RootWidget(ScreenManager):
    pass

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        return RootWidget()

MainApp().run()