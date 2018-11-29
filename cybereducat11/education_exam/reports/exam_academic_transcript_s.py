# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import fields, models,api
import pandas as pd


class acdemicTranscripts(models.AbstractModel):
    _name = 'report.education_exam.report_exam_academic_transcript_s'
    def get_exams(self, objects):
        obj = []
        for object in objects.exams:
           obj.extend(object)

        return obj
    def get_students(self,objects):

        student=[]
        if objects.specific_student==True :
            student_list = self.env['education.class.history'].search([('student_id.id', '=', objects.student.id),('academic_year_id.id', '=', objects.academic_year.id)])
            for stu in student_list:
                student.extend(stu)
        elif objects.section:
            student_list=self.env['education.class.history'].search([('class_id.id', '=', objects.section.id)])
            for stu in student_list:
                student.extend(stu)
        elif objects.level:
            student_list = self.env['education.class.history'].search([('level.id', '=', objects.level.id),
                                                                       ('academic_year_id.id', '=', objects.academic_year.id)])
            for stu in student_list:
                student.extend(stu)

        return student

    def get_subjects(self,student,object,selection_type,evaluation_type):
        student_history=self.env['education.class.history'].search([('id', '=', student.id),('academic_year_id',"=",object.academic_year.id)])
        subjs = []
        if selection_type=='non_optional':
            for subj in student_history.compulsory_subjects:
                if subj.evaluation_type==evaluation_type :
                    subjs.extend(subj)
            for subj in student_history.selective_subjects:
                if subj.evaluation_type==evaluation_type:
                    subjs.extend(subj)
        else:
            for subj in student_history.optional_subjects:
                subjs.extend(subj)

        return subjs
    def get_optional_subjects(self,student_history,object):
        # student_history = self.env['education.class.history'].search(
        #     [('id', '=', student.id), ('academic_year_id', "=", object.academic_year.id)])
        subjs = []
        for subj in student_history.optional_subjects:
            subjs.extend(subj)
        return subjs
    def count_subjects(self,student_history,object,optional):
        count = 0
        if optional=='optional':
            for subj in student_history.optional_subjects:
                count=count+0
        else:
            for subj in student_history.compulsory_subjects:
                count = count + 0
            for subj in student_history.selective_subjects:
                count = count + 0
        return count
    def get_gradings(self,obj):
        grading=self.env['education.result.grading'].search([('id','>','0')],order='min_per desc',)
        grades=[]
        for grade in grading:
            grades.extend(grade)
        return grades
    def get_marks(self,exam,subject,student_history):
        student=student_history.student_id
        marks=self.env['results.subject.line'].search([('exam_id','=',exam.id),('subject_id','=',subject.id),('student_id','=',student.id)])
        return marks

    def get_exam_obtained_total(self,exam,student_history,optional,evaluation):
        student = student_history.student_id
        marks = self.env['results.subject.line'].search(
            [('exam_id', '=', exam.id),('student_id', '=', student.id)])
        total=0
        general=0
        extra=0

        if optional=='optional':
            for subject in marks:
                if subject.subject_id in student_history.optional_subjects:
                    total=total+ subject.mark_scored

        elif evaluation=='general':
            for subject in marks:
                if subject.subject_id not in student_history.optional_subjects:
                    if subject.subject_id.evaluation_type == 'general':
                        total=total+ subject.mark_scored
        elif evaluation=='extra':
            for subject in marks:
                if subject.subject_id not in student_history.optional_subjects:
                    if subject.subject_id.evaluation_type=='extra':
                        total=total+subject.mark_scored
        return total
    def get_exam_total(self,exam,student_history,optional,evaluation):
        student = student_history.student_id
        marks = self.env['results.subject.line'].search(
            [('exam_id', '=', exam.id), ('student_id', '=', student.id)])
        total = 0
        if optional == 'optional':
            for subject in marks:
                if subject.subject_id in student_history.optional_subjects:
                    total = total + subject.subject_id.total_mark

        elif evaluation == 'general':
            for subject in marks:
                if subject.subject_id not in student_history.optional_subjects:
                    if subject.subject_id.evaluation_type == 'general':
                        total = total + subject.subject_id.total_mark
        elif evaluation == 'extra':
            for subject in marks:
                if subject.subject_id not in student_history.optional_subjects:
                    if subject.subject_id.evaluation_type == 'extra':
                        total = total + subject.subject_id.total_mark
        return total

    def get_highest(self,exam,subject):
        highest = self.env['results.subject.line'].search(
            [('exam_id', '=', exam.id), ('subject_id', '=', subject.id)], limit=1, order='mark_scored DESC')
        return highest
    def get_gpa(self,student_history,exam,optional,evaluation_type):
        student = student_history.student_id
        gp=0
        count=0
        records = self.env['results.subject.line'].search(
            [('exam_id', '=',exam.id ),  ('student_id', '=', student.id)])

        for rec in records:
            if optional !="optional":
                if evaluation_type=='general':
                    if rec.subject_id not in student_history.optional_subjects :
                        if rec.subject_id.evaluation_type=='general':
                            gp=gp+ rec.grade_point
                            count=count+1
                if evaluation_type=='extra':
                    if rec.subject_id not in student_history.optional_subjects :
                        if rec.subject_id.evaluation_type=='extra':
                            gp=gp+ rec.grade_point
                            count=count+1


            elif rec.subject_id  in student_history.optional_subjects:
                    gp = gp + rec.grade_point
                    count = count + 1

        if count==0:
            return 0
        else :
            return round(gp/count,2)
        # float("{0:.2f}".format(gp/count))

    def get_merit_list(self,object):
        list=[]
        stu=[]
        total_scor=[]
        exa=[]
        section=[]
        merit_class=[]
        merit_section=[]
        index=1
        student_list=[]
        for exam in object.exams:
            exa=[]
            scor=[]
            merit_class=[]
            merit_section=[]
            fail_in_extra=[]
            if index==1:
                student_list = self.env['education.class.history'].search([('level.id', '=', object.level.id)])
            for student in student_list:
                obtained_total=0
                optional_obtained=0
                extra_obtained=0
                optional_count=0
                optional_total=0
                fail_extra=1
                mark_line = self.env['results.subject.line'].search(
                    [('student_id', '=', student.student_id.id), ('exam_id', '=', exam.id)])
                for line in mark_line:
                    # filter the subject is not optional for the student
                    if line.subject_id  not in student.optional_subjects:
                        if line.subject_id.evaluation_type != 'extra':
                            if line.mark_scored:
                                obtained_total=obtained_total+line.mark_scored
                        elif line.mark_scored:
                            extra_obtained=extra_obtained+line.mark_scored
                            if line.letter_grade=='F':
                                fail_extra=0

                    elif line.mark_scored:
                        optional_count=optional_count+1
                        optional_total=optional_total+line.subject_id.total_mark
                        optional_obtained=optional_obtained+line.mark_scored
                additional_mark=optional_obtained-(optional_total*0.4)
                if additional_mark>0:
                    obtained_total=obtained_total+additional_mark
                section.append(student.section.id)
                stu.append(student.student_id.id)
                exa.append(exam.id)
                scor.append(obtained_total)
                merit_class.append(0)
                merit_section.append(0)
                fail_in_extra.append(fail_extra)
            if index==1:
                data={'student':stu,'section':section,"exam"+ str(index) :exa,
                      'Score'+ str(index) :scor,'merit_class'+ str(index) :merit_class,'merit_section'+ str(index) :merit_section,
                      'Score': scor, 'merit_class': merit_class,
                      'merit_section' : merit_section,'fail_in_extra':fail_in_extra}
                df= pd.DataFrame(data)
            else:
                df.insert(3, 'exam'+str(index), exa, allow_duplicates=False)
                df.insert(4, 'Score'+str(index), scor, allow_duplicates=False)
                df.insert(4, 'merit_class'+str(index), merit_class, allow_duplicates=False)
                df.insert(4, 'merit_section'+str(index), merit_section, allow_duplicates=False)

            result = df.sort_values(by=['Score'+str( index) ], ascending=False)
            result=result.reset_index(drop=True)
            for i in range(0,len(result)):
                df.loc[df[ 'student' ] == result.at[i,'student'], 'merit_class'+ str(index) ] = i+1
                if index>1:
                    df.loc[df[ 'student' ] == result.at[i,'student'], 'Score' ] = result.at[i,'Score']+result.at[i,'Score'+str(index)]
                # result.at[i,'merit_class']=i+1
                i=i+1
            section_list=df.section.unique()
            for rec in section_list:
                df1 = df[(df['section'] ==rec )]
                result = df1.sort_values(by=['Score'+str (index) ,'fail_in_extra'], ascending=[False,False])
                result = result.reset_index(drop=True)
                for i in range(0, len(result)):
                    df.loc[df['student'] == result.at[i, 'student'], 'merit_section'+str (index) ] = i + 1
                    # result.at[i, 'merit_section'] = i + 1
                    i = i + 1
            index = index + 1
        result = df.sort_values(by=['Score','fail_in_extra'], ascending=[False,False])
        result = result.reset_index(drop=True)
        for i in range(0, len(result)):
            df.loc[df['student'] == result.at[i, 'student'], 'merit_class'] = i + 1

            # result.at[i,'merit_class']=i+1
            i = i + 1
        section_list = df.section.unique()
        for rec in section_list:
            df1 = df[(df['section'] == rec)]
            result = df1.sort_values(by=['Score'], ascending=False)
            result = result.reset_index(drop=True)
            for i in range(0, len(result)):
                df.loc[df['student'] == result.at[i, 'student'], 'merit_section'] = i + 1
                # result.at[i, 'merit_section'] = i + 1
                i = i + 1


        return df

    def num2serial(self,numb):
        if numb < 20:  # determining suffix for < 20
            if numb == 1:
                suffix = 'st'
            elif numb == 2:
                suffix = 'nd'
            elif numb == 3:
                suffix = 'rd'
            else:
                suffix = 'th'
        else:  # determining suffix for > 20
            tens = str(numb)
            tens = tens[-2]
            unit = str(numb)
            unit = unit[-1]
            if tens == "1":
                suffix = "th"
            else:
                if unit == "1":
                    suffix = 'st'
                elif unit == "2":
                    suffix = 'nd'
                elif unit == "3":
                    suffix = 'rd'
                else:
                    suffix = 'th'
        return str(numb) + suffix

    def get_row_count(self,student_history,exam):
        student = student_history.student_id
        count=0
        records = self.env['results.subject.line'].search(
            [('exam_id', '=',exam.id ),  ('student_id', '=', student.id)])
        for rec in records:
            count=count+1
        return count
    def get_date(self, date):
        date1 = datetime.strptime(date, "%Y-%m-%d")
        return str(date1.month) + ' / ' + str(date1.year)

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['academic.transcript'].browse(docids)
        return {
            'doc_model': 'education.exam.results',
            'docs': docs,
            'time': time,
            'get_students': self.get_students,
            'get_exams': self.get_exams,
            'get_subjects': self.get_subjects,
            'get_gradings':self.get_gradings,
            'get_marks':self.get_marks,
            'get_merit_list':self.get_merit_list,
            'get_date': self.get_date,
            'get_highest': self.get_highest,
            'get_gpa': self.get_gpa,
            'get_row_count': self.get_row_count,
            'get_optional_subjects': self.get_optional_subjects,
            'get_exam_total': self.get_exam_total,
            'get_exam_obtained_total': self.get_exam_obtained_total,
            'count_subjects': self.count_subjects,
            'num2serial': self.num2serial,
        }
