# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import fields, models,api


class acdemicTranscript(models.AbstractModel):
    _name = 'report.education_exam.report_exam_academic_transcript'

    def get_exams(self, objects):
        obj = []
        for object in objects.exams:
           obj.extend(object)

        return obj
    def get_students(self,objects):
        student=[]
        if objects.specific_student==True :
            for stu in objects.student:
                student.extend(stu)

        return student

    def get_subjects(self, obj,result_type):
        object=self.env['education.exam.results'].browse(obj.id)
        subjs = []
        for subj in object.subject_line:
            if subj.subject_id.evaluation_type==result_type:
                subjs.extend(subj)
        return subjs
    def get_gradings(self,obj):
        grading=self.env['education.result.grading'].search([('id','>','0')],order='min_per desc',)
        grades=[]
        for grade in grading:
            grades.extend(grade)
        return grades


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
            'get_date': self.get_date,
            # 'get_total': self.get_total,
        }
