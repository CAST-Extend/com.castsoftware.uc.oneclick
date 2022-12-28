from discovery.sourceValidation import SourceValidation 
from pandas import DataFrame,read_excel
import docx
from config import Config

class DiscoveryReport(SourceValidation):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        
    def run(cls,config:Config):
        for appl in config.application:



            # read by 'Stats Before Code CleanUP' sheet of an Cloc_Output excel file
            df = read_excel(output_path+f"\\Cloc_Output_{sourceDiscovery.file_suffix}.xls",sheet_name='Stats Before Code CleanUP')
            
            #extract total cout of applicable code from 'Stats Before Code CleanUP' sheet of an Cloc_Output excel file
            filt=(df['APPLICABLE']=='YES')
            pre_LOC=(df.loc[filt,'CODE'].sum())
            pre_LOC=pre_LOC//1000
            #print(pre_LOC)

            filt=(df['APPLICABLE']=='NO')
            l=df.loc[filt,['LANGUAGE','CODE']].sort_values(by=['CODE'], ascending=False) 
            non_code=''
            if len(l) == 1:
                non_code= str(l.iloc[0]['CODE']//1000) +' KLOC of '+ l.iloc[0]['LANGUAGE']
            elif len(l) > 1:
                non_code= str(l.iloc[0]['CODE']//1000) +' KLOC of '+ l.iloc[0]['LANGUAGE'] +' non code files and ~'+ str(l.iloc[1]['CODE']//1000) +' KLOC of '+ l.iloc[1]['LANGUAGE']

            # read by 'Stats After Code CleanUP' sheet of an Cloc_Output excel file
            df2 = pd.read_excel(output_path+f"\\Cloc_Output_{sourceDiscovery.file_suffix}.xls",sheet_name='Stats After Code CleanUP')
            
            #extract total count of applicable code from 'Stats After Code CleanUP' sheet of an Cloc_Output excel file
            filt=(df2['APPLICABLE']=='YES')
            post_LOC=(df2.loc[filt,'CODE'].sum())
            post_LOC=post_LOC//1000
            #print(post_LOC)

            # read by 'Summary' sheet of an SQL_Output excel file
            df3 = pd.read_excel(output_path+f"\\SQL_Output_{sourceDiscovery.file_suffix}.xls",sheet_name='Summary')
            table_count = df3.iloc[0]['COUNT']
            procedure_count = df3.iloc[1]['COUNT']
            function_count = df3.iloc[2]['COUNT']
            triggers_count = df3.iloc[3]['COUNT']

            # create an instance of a word document
            doc = docx.Document()

            # add a heading of level 0 (largest heading)
            doc.add_heading('Source code discovery report', 0)

            # add a paragraph and store
            # the object in a variable
            doc_para = doc.add_paragraph('Please find below the completed discovery for the Project Plough')

            doc.add_heading('Application Orlo :', 1)
            doc_para = doc.add_paragraph('•	The delivered code was computed as ~'+str(pre_LOC)+' KLOC using CLOC. ')
            doc_para = doc.add_paragraph('•	The delivered code contains ~'+non_code+' non code files which will be out of scope of analysis.')
            doc_para = doc.add_paragraph('•	Post cleanup of test code, the LOC is further reduced to ~'+str(post_LOC)+' KLOC. ')
            doc_para = doc.add_paragraph('•	Folders like Test code, sample code, node modules, examples etc. will be excluded from the scope of analysis. ')
            doc_para = doc.add_paragraph('•	There is a total of '+str(int(table_count))+' tables, '+str(int(function_count))+' function, '+str(int(procedure_count))+' stored procedures and '+str(int(triggers_count))+' triggers in the database.')
            doc_para = doc.add_paragraph('•	LOC split on technology level is provided below. ')

            #extracting table data from cloc_oupt excel sheet.
            filt=(df2['APPLICABLE']=='YES')
            t_df=df2.loc[filt,['LANGUAGE','FILES','CODE']]
            t_df.loc[len(t_df.index)] = ['Total', t_df['FILES'].sum() , t_df['CODE'].sum()] 

            # add a table to the end and create a reference variable
            # extra row is so we can add the header row
            t = doc.add_table(t_df.shape[0]+1, t_df.shape[1])

            # add the header rows.
            for j in range(t_df.shape[-1]):
                t.cell(0,j).text = t_df.columns[j]

            # add the rest of the data frame
            for i in range(t_df.shape[0]):
                for j in range(t_df.shape[-1]):
                    t.cell(i+1,j).text = str(t_df.values[i,j])
            
            # Adding style to a table
            t.style = 'Light List Accent 1'

            # now save the document to a location
            doc.save(output_path+f'\Source code discovery_{sourceDiscovery.file_suffix}.docx')
            print('MS Word Document has been generated and available in the location -> '+output_path)

