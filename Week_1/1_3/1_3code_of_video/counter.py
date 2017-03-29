# coding=utf-8

import requests
import re
from bs4 import BeautifulSoup


class course(object):
    def __init__(self, c1='0', c2='0', cn='0', ce='0', cr='0', ca='0', cg='0'):
        self.CourseNumber1 = c1
        self.CourseNumber2 = c2
        self.CourseName = cn
        self.CourseEnglishName = ce
        self.CourseCredit = cr
        self.CourseAttribute = ca
        self.CourseGrade = cg

    def get_CourseNumber1(self):
        return self.CourseNumber1

    def get_CourseName(self):
        return self.CourseName

    def get_CourseCredit(self):
        return self.CourseCredit

    def get_CourseGrade(self):
        return self.CourseGrade

    def get_Mul(self):
        return float(self.CourseGrade) * float(self.CourseCredit)

    def change_CourseGrade(self, grade):
        self.CourseGrade = grade

    def change_CourseName(self, name):
        self.CourseName = name

    def change_CourseCredit(self, credit):
        self.CourseCredit = credit


class UesrLogin(object):
    def __init__(self):
        self.params = {'zjh': None, 'mm': None}

    def UserInfoGet(self,user,password):
        self.params['zjh'] = user
        self.params['mm'] = password

    def UrpLogin(self):
        session = requests.Session()
        s = session.post("http://urpjw.cau.edu.cn/loginAction.do", self.params, headers={"user-agent": "Chrome/10"})
        s = session.get("http://urpjw.cau.edu.cn/xjInfoAction.do?oper=xjxx")
        bsObj_PersonalInformation = BeautifulSoup(s.text, 'lxml')
        s = session.get(
            "http://urpjw.cau.edu.cn/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2015-2016%D1%A7%C4%EA%C7%EF(%C8%FD%D1%A7%C6%DA)")
        bsObj_PerformanceInformation = BeautifulSoup(s.text, 'lxml')
        return bsObj_PersonalInformation, bsObj_PerformanceInformation


class psI(object):  # personalInformation class
    def PersonalInformation(self, bsObj):
        yourName = bsObj.findAll(id="tblView")[0].findAll("tr")[0].findAll("td")[3].get_text().strip()
        #print('#' + yourName + '#')
        yourClass = bsObj.findAll(id="tblView")[0].findAll("tr")[14].findAll("td")[3].get_text().strip()
        #print('#' + yourClass + '#')
        return {'yourName':yourName,'yourClass':yourClass}


class pfI(object):  # performanceInformation class
    def PerformanceInformation(self, bsObj):
        CourseDetailsList = []

        for CourseDetailsHTML in bsObj.find_all('td', align="center"):
            CourseDetailsText = CourseDetailsHTML.get_text()
            CourseDetailsList.append(re.sub('\s', '', CourseDetailsText))

        # print(CourseDetailsList)


        LessonList = []

        for i in range(int(len(CourseDetailsList) / 7)):
            LessonList.append("%s" % i)
            try:
                LessonList[i] = course(CourseDetailsList[i * 7], CourseDetailsList[i * 7 + 1],
                                       CourseDetailsList[i * 7 + 2], CourseDetailsList[i * 7 + 3],
                                       CourseDetailsList[i * 7 + 4], CourseDetailsList[i * 7 + 5],
                                       CourseDetailsList[i * 7 + 6])
            except IndexError:
                pass
        # print(LessonList[0].CourseNumber1)

        return LessonList

        #print(LessonList[0].CourseNumber1+LessonList[0].CourseName+
        #LessonList[0].CourseCredit+LessonList[0].CourseAttribute+LessonList[0].CourseGrade)

    def grade_change(self, grade_before):
        if grade_before == '优秀':
            grade = 4.0
            return grade
        if grade_before == '良好':
            grade = 3.7
            return grade
        if grade_before == '中等':
            grade = 2.7
            return grade
        if grade_before == '及格':
            grade = 2.0
            return grade
        if grade_before == '不及格':
            grade = 0.0
            return grade
        else:
            try:
                float(grade_before)
            except (ValueError, TypeError):
                return 0
            if grade_before == 'A' or float(grade_before) in range(90, 750):
                grade = 4.0
                return grade
            if grade_before == 'A-' or float(grade_before) in range(85, 90):
                grade = 3.7
                return grade
            if grade_before == 'B+' or float(grade_before) in range(82, 85):
                grade = 3.3
                return grade
            if grade_before == 'B' or float(grade_before) in range(78, 82):
                grade = 3.0
                return grade
            if grade_before == 'B-' or float(grade_before) in range(75, 78):
                grade = 2.7
                return grade
            if grade_before == 'C+' or float(grade_before) in range(72, 75):
                grade = 2.3
                return grade
            if grade_before == 'C' or float(grade_before) in range(68, 72):
                grade = 2.0
                return grade
            if grade_before == 'C-' or float(grade_before) in range(64, 68):
                grade = 1.5
                return grade
            if grade_before == 'D' or float(grade_before) in range(60, 64):
                grade = 1.0
                return grade
            if grade_before == 'F' or float(grade_before) in range(0, 60):
                grade = 0.0
                return grade

    def gpaCounter(self, bsObj):

        LessonList = self.PerformanceInformation(bsObj)


        # 将双学位和英语四六级对应的学分转换为0
        for i in range(len(LessonList)):
            if LessonList[i].get_CourseName().find('双学位') > -1:  # 当在CourseName中找不到指定字符串是，返回值为-1
                LessonList[i].change_CourseCredit(0)
            if LessonList[i].get_CourseName().find('CET') > -1:
                LessonList[i].change_CourseCredit(0)


        for i in range(len(LessonList)):
            LessonList[i].change_CourseGrade(self.grade_change(LessonList[i].get_CourseGrade()))

        SumCreMulGra = float(0)
        SumCredit = float(0)
        for i in range(len(LessonList)):
            if LessonList[i].CourseAttribute == '必修':
                SumCreMulGra = SumCreMulGra + LessonList[i].get_Mul()
                SumCredit = SumCredit + float(LessonList[i].get_CourseCredit())
        requiredGPA = '%.2f' % (SumCreMulGra / SumCredit)


        SumCreMulGra = float(0)
        SumCredit = float(0)
        for i in range(len(LessonList)):
            if LessonList[i].CourseAttribute == '选修':
                SumCreMulGra = SumCreMulGra + LessonList[i].get_Mul()
                SumCredit = SumCredit + float(LessonList[i].get_CourseCredit())
        electiveGPA = '%.2f' % (SumCreMulGra / SumCredit)

        SumCreMulGra = float(0)
        SumCredit = float(0)
        for i in range(len(LessonList)):
            SumCreMulGra = SumCreMulGra + LessonList[i].get_Mul()
            SumCredit = SumCredit + float(LessonList[i].get_CourseCredit())
        totalGPA = '%.2f' % (SumCreMulGra / SumCredit)

        return SumCredit,requiredGPA,electiveGPA,totalGPA



