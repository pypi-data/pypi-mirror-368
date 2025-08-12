from IPython.core.magic import (Magics, line_magic, cell_magic, magics_class)
import requests
from IPython.display import display, HTML
import ipywidgets as widgets
from ipywidgets import Layout, Button, HBox, VBox
import traceback 
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode


@magics_class
class dmt(Magics):
    
    dmt_url = None
    default_repo = None

    def __init__(self, shell):
        super(dmt, self).__init__(shell)
    

    def __createTextAnswer (self):
        input_answer = widgets.Textarea(value='', placeholder='SQL-Code ...', layout = Layout(width = '95%', height = '10em'))
        return VBox([input_answer]), lambda : input_answer.value


    def __createTableAnswer (self):
        cells = [[widgets.Text(value='', disabled=False, layout = widgets.Layout(width='8em')) for col in range(5)] for row in range(8)]
        cells[0][0].placeholder = "Attributname ..."
        cells[1][0].placeholder = "Attributwert ..."
        horLine = widgets.HTML(value='<hr style="border:1px solid black; padding:0; margin:0">')
        answerFunc = lambda : "\n".join (["\t".join ([c.value for c in row]) for row in cells ])
        return VBox([HBox(cells[0]), horLine] + [HBox(row) for row in cells[1:]]), answerFunc

    def __createSchemaAnswer (self):
        attributes = [widgets.Text(value='') for i in range(6)]
        primary = [widgets.Checkbox(value=False, indent=False, layout = Layout(justify_content='center')) for i in range(6)]
        foreign = [widgets.Checkbox(value=False, indent=False, layout = Layout(justify_content='center')) for i in range(6)]

        layout = Layout(width='100%', align_items='center')
        box = HBox([
            VBox([widgets.Label(value="Attributname")] + attributes, layout = layout),
            VBox([widgets.Label(value="Primärschlüssel")] + primary, layout = layout),
            VBox([widgets.Label(value="Fremdschlüssel")] + foreign, layout = layout)
        ])

        answerFunc = lambda : "\n".join ("" if a.value.strip()=="" else f"{a.value.strip()}\t{int(p.value)}\t{int(f.value)}" for a, p, f in zip(attributes, primary, foreign))
        return box, answerFunc


    @cell_magic("dmt")
    def dmtCell(self, line, cell):
        # Check result with DMT: line = taskid; cell = answer
        try:        
            taskid = line
            answer = cell.lstrip()
            if answer.upper().startswith("%SQL"): answer = answer[4:]
            if answer.upper().startswith("%%SQL"): answer = answer[5:]
            if answer.upper().startswith("%%MARKDOWN"): 
                answer = answer[10:]
                md = MarkdownIt("commonmark").enable('table')
                tokens = md.parse(answer)

                duringTable = False
                answer = ""
                for t in tokens:
                    match t.type:
                        case "table_open": duringTable = True
                        case "table_close": duringTable = False
                        case "tr_close": 
                            if duringTable : answer = answer + "\n"
                        case "td_close" | "th_close": 
                            if duringTable : answer = answer + "\t"
                        case "inline": 
                            if duringTable : answer = answer + t.content

                # print (answer)
                # for t in tokens: print (t)
                

            response = requests.post(
                url = self.dmt_url + "/gettaskresult", 
                params=  { "taskid" : taskid, "answer": answer}, 
                headers= { "Content-Type" : "application/json" }).json()
            display  (HTML(f'<div class="alert alert-warning">{response["feedback"]} ({response["points"]} von {response["points_max"]} Punkten)</div>'))   
        except Exception:
            display  (HTML ('<div class="alert alert-warning">DMT check failed</div>'))
        
        # Execute cell content (e.g. SQL code or Markdown)  
        self.shell.run_cell(cell, store_history=False)


    @line_magic("dmt")
    def dmtLine(self, line):
        
        taskID = line.strip()

        # set DMT url
        if taskID.lower().startswith("url="):
            self.dmt_url = taskID[4:]
            display  (HTML(f'<div class="alert alert-warning">Set DMT URL to {self.dmt_url}</div>'))
            return

        response = requests.post(
            url = self.dmt_url + "/gettaskinfo", 
            params = { "taskid" : taskID },  
            headers = { "Content-Type" : "application/json" }).json()

        # print (response)

        # show question
        display(HTML(response['question']))

        # show answer area and status
        answerType = {
            "SELECT":   self.__createTextAnswer,
            "VIEW":     self.__createTextAnswer,
            "CHECK":    self.__createTextAnswer,
            "SCHEMA":   self.__createSchemaAnswer,
            "TABLE":    self.__createTableAnswer
        }
        answerBox, checkFunction = answerType.get(response['tasktype'])()
        display (answerBox)
        display (HTML("<code>" + response['status'] + "</code>"))


        # show button and output
        button = widgets.Button(description="Abgabe Überprüfen", button_style='info')
        output = widgets.Output()

        def on_button_clicked(b):
            with output:
                output.clear_output()
                response = requests.post(
                    url = self.dmt_url + "/gettaskresult", 
                    params=  { "taskid" : taskID, "answer": checkFunction()}, 
                    headers= { "Content-Type" : "application/json" }).json()

                print(response['feedback'])
                print(f"Punkte: {response['points']} von {response['points_max']}")

        button.on_click(on_button_clicked)
        display (button, output)


def load_ipython_extension(ipython):
    ipython.register_magics(dmt)
