# -*- coding: utf-8 -*-


from odoo import models, fields, api


class EducationExamResults(models.Model):
    _name = 'education.exam.results'

    name = fields.Char(string='Name')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    student_id = fields.Many2one('education.student', string='Student')
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('results.subject.line', 'result_id', string='Subjects')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    total_pass_mark = fields.Integer(string='Total Pass Mark', store=True, readonly=True, compute='_total_marks_all')
    total_max_mark = fields.Integer(string='Total Max Mark', store=True, readonly=True, compute='_total_marks_all')
    total_mark_scored = fields.Integer(string='Total Marks Scored', store=True, readonly=True, compute='_total_marks_all')
    overall_pass = fields.Boolean(string='Overall Pass/Fail', store=True, readonly=True, compute='_total_marks_all')
    @api.depends('subject_line.mark_scored')
    def _total_marks_all(self):
        for results in self:
            total_pass_mark = 0
            total_max_mark = 0
            total_mark_scored = 0
            overall_pass = True
            for subjects in results.subject_line:
                total_pass_mark += subjects.pass_mark
                total_max_mark += subjects.max_mark
                total_mark_scored += subjects.mark_scored
                if not subjects.pass_or_fail:
                    overall_pass = False
            results.total_pass_mark = total_pass_mark
            results.total_max_mark = total_max_mark
            results.total_mark_scored = total_mark_scored
            results.overall_pass = overall_pass


class ResultsSubjectLine(models.Model):
    _name = 'results.subject.line'

    tut_mark = fields.Integer(string='Tutorial')
    subj_mark = fields.Integer(string='Subjective')
    obj_mark = fields.Integer(string='Objective')
    prac_mark = fields.Integer(string='Practical')
    letter_grade=fields.Char('Grade')
    grade_point=fields.Float('GP')
    name = fields.Char(string='Name')
    subject_id = fields.Many2one('education.syllabus', string='Subject')
    max_mark = fields.Integer(string='Max Mark')
    pass_mark = fields.Integer(string='Pass Mark')
    mark_scored = fields.Integer(string='Mark Scored')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    result_id = fields.Many2one('education.exam.results', string='Result Id')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    student_id = fields.Many2one('education.student', string='Student')
    student_name = fields.Char(string='Student')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

class exam_result_summery(models.Model):
    _name = 'education.exam.student.summary'
    exam_id =fields.Many2one('education.exam','Exam')
    student_id=fields.Many2one('education.student',string='Student')
    total_mark=fields.Integer('Total')
    total_gpa=fields.Many2one('education.result.grading', 'Total GPA')
    total_lg=fields.Integer( 'Total GPA')
    additional_mark=fields.Integer('additional')
    additional_gpa = fields.Many2one('education.result.grading', 'additional GPA')
    additional_lg = fields.Integer( 'additional Grade')
    extra_mark=fields.Integer('Extra')
    extra_gpa = fields.Many2one('education.result.grading', 'Extra GPA')
    extra_lg = fields.Integer('Extra Grade')
    net_mark=fields.Integer('net')
    net_gpa = fields.Many2one('education.result.grading', 'NET GPA')
    net_lg = fields.Integer('GPA')
    position_class=fields.Integer("Position in Class")
    position_section=fields.Integer("Position in Section")