from flask import Flask, render_template, request, jsonify, flash, redirect, session, abort
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms.fields import DateField
import os
import shutil
import sys
from cryptography.fernet import Fernet
from pymysql import connect
from datetime import datetime
import json

# sys.path.insert(0, '//NAS/PFX_PROJECTS/PIPELINE_FILES/pfxdb')
# from dbconnect import get_all, dbconect

app = Flask(__name__)from astroid.__pkginfo__ import web

bootstrap = Bootstrap(app)
UPLOAD_FOLDER = 'D:/PROJECTS/bids'
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
else:
    pass


class MyForm(Form):
    date = DateField(id='datepick')


def dbconect(sql):
    result = []
    db = connect(host='192.168.2.90', database='pfxdb', user='pipe', password='asdf$123')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    for i in cursor.fetchall():
        result.append(i[0])
    cursor.close()
    return result


def get_all(sql):
    result = []
    db = connect(host='192.168.2.90', database='pfxdb', user='pipe', password='asdf$123')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    for i in cursor.fetchall():
        result.append(i)
    cursor.close()
    return result

def get_lcl(sql):
    result = []
    db = connect(host='localhost', database='test', user='root', password='1234')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    for i in cursor.fetchall():
        result.append(i)
    cursor.close()
    return result

def get_artistID(login):
    """find artist ID with the help of their workstation login"""
    try:
        sql = "SELECT artist_id from artist where login='{0}'".format(str(login))
        artistID = dbconect(sql)[0]
        return artistID
    except IndexError:
        return []


def collect_typename(typeID):
    try:
        sql = "SELECT type_name from type where type_id={0}".format(typeID)
        tasktype = dbconect(sql)[0]
        return tasktype
    except IndexError:
        return []


def collect_projName(projID):
    """return project ID for project name or code"""
    try:
        sql = "SELECT proj_code from project_settings WHERE proj_id='{0}'".format(projID)
        list_projName = dbconect(sql)[0]
        return list_projName
    except IndexError:
        return []


def collect_scopeName(scopeID):
    """given scopeName, return corresponding scope ID"""
    try:
        sql = "SELECT scope_name from scope WHERE scope_id={0}".format(scopeID)
        scopeName = dbconect(sql)[0]
        return scopeName
    except IndexError:
        return []


def collect_statusName(task_status_id):
    try:
        sql = "SELECT task_status_name from task_status where task_status_id={0}".format(task_status_id)
        statusName = dbconect(sql)[0]
        return statusName
    except IndexError:
        return []


def get_pfxdb_notes(pub_id):
    '''function to return list of tuples containing reviewer name,notes,& attachment'''
    pfxdb_notes = []
    reviewer_list = []
    notes_list = []
    attachment_list = []

    for i in pub_id:
        sql = "SELECT reviewer_name,notes,attachment from notes where publish_id='{0}'".format(i)
        res = get_all(sql)
        if res != []:
            for j in res:
                reviewer_list.append(j[0])
                notes_list.append(j[1])
                attachment_list.append(j[2])

            temp = (i, reviewer_list, notes_list, attachment_list)
            pfxdb_notes.append(temp)
        else:
            temp = (i, '', '', '')
            pfxdb_notes.append(temp)

    return pfxdb_notes


def get_task_details(userLogin):
    '''function to get task assigned to artist'''
    artID = get_artistID(userLogin)
    sql = "SELECT * from task where assigned_to={0}".format(artID)
    res = get_all(sql)
    version_dict = []
    notes_dict = []
    p_res = []
    for i in res:
        i = list(i)
        task_id = i[0]
        proj_id = i[1]
        scope_id = i[2]
        type_id = i[3]
        pub_id = get_publish_id(task_id)
        ver = get_pfxdb_version(pub_id)
        version_dict.append(ver)
        notes = get_pfxdb_notes(pub_id)
        notes_dict.append(notes)

        ##### HTML link replacing and downloading or opening the link upon clicking in browser ########
        import os
        import shutil
        # paths = []
        try:
            for attachment in notes_dict[0][1][3]:
                print(attachment)
                if os.path.exists(attachment):

                    filename = os.path.basename(attachment)

                    global new_file_path
                    new_file_path = "D:/Murthy/Git_Projects/webmodules/login/static/tempfiles/" + filename
                    try:
                        files = shutil.copy(attachment, new_file_path)
                    except:
                        pass
                    if filename == os.path.basename(new_file_path):

                        if attachment == attachment in notes_dict[0][1][3]:
                            #
                            index = notes_dict[0][1][3].index(attachment)

                            notes_dict[0][1][3].remove(attachment)
                            notes_dict[0][1][3].insert(index, filename)
                #
                else:
                    print("Path does not exist")

        except IndexError:
            pass
        ##### HTML #######

        if type_id == 0:
            sql = "SELECT task_type_name from task where task_id={0}".format(task_id)
            res = dbconect(sql)[0]
            i[3] = res.upper()
        elif type(type_id) == int:
            type_name = collect_typename(type_id)
            i[3] = type_name.upper()

        user = i[12]
        frame_start = i[5]
        frame_end = i[6]
        description = i[7]
        # emd = i[10]
        # cmd = i[11]
        task_status = i[16]
        bid_start = i[17]
        bid_end = i[18]

        if task_id != 0:
            proj = collect_projName(proj_id)
            scope = collect_scopeName(scope_id)
            status = collect_statusName(task_status)
            i[1] = proj
            i[2] = scope
            i[16] = status
            try:
                i[18] = i[18].date().strftime('%d-%m-%Y')
            except AttributeError:
                i[18] = i[18].split()[0]
                end_date = i[18].split('-')[2]
                end_mnth = i[18].split('-')[1]
                end_yr = i[18].split('-')[0]
                i[18] = end_date + '-' + end_mnth + '-' + end_yr

            indexes = [4, 8, 9, 10, 11, 12, 13, 14, 15, 17]
            for index in sorted(indexes, reverse=True):
                del i[index]
            p_res.append(i)
        #

        else:
            proj = collect_projName(proj_id)
            scope = collect_scopeName(scope_id)
            status = collect_statusName(task_status)
            i[1] = proj
            i[2] = scope
            i[16] = status
            try:

                i[18] = i[18].date().strftime('%d-%m-%Y')
            except AttributeError:
                i[18] = i[18].split()[0]
                end_date = i[18].split('-')[2]
                end_mnth = i[18].split('-')[1]
                end_yr = i[18].split('-')[0]
                i[18] = end_date + '-' + end_mnth + '-' + end_yr

            indexes = [4, 8, 9, 10, 11, 12, 13, 14, 15]
            for index in sorted(indexes, reverse=True):
                del i[index]
            p_res.append(i)

    # print(notes_dict)
    return p_res, version_dict, notes_dict


def collect_projID(projName):
    '''returning corresponding project ID of project codes/names'''
    try:
        sql = "SELECT proj_id from project_settings WHERE proj_code='{0}'".format(projName)
        list_projID = dbconect(sql)[0]
        return list_projID
    except IndexError:
        return []


def collect_scopID(scopeName, projid):
    '''return scope_id of scope_name'''
    try:
        sql = "SELECT scope_id from scope WHERE scope_name LIKE '%{0}' AND proj_id='{1}'".format(scopeName, projid)
        list_scopeID = dbconect(sql)[0]
        return list_scopeID
    except IndexError:
        return []


def collect_typeID(typeName):
    '''find type id for type name'''
    try:
        sql = "SELECT type_id from type WHERE type_name='{0}'".format(typeName)
        task_id = dbconect(sql)[0]
        return task_id
    except IndexError:
        return []


def get_publish_id(taskID):
    '''get list of publishes made against the specific task'''
    pub_id = []
    sql = "SELECT publish_id from publish_q where task_id={0}".format(taskID)
    res = dbconect(sql)
    return res


def get_pfxdb_version(pub_id):
    '''get internal versions from db based on the publish IDs by looping through their list'''
    pfxdb_version = []
    for i in pub_id:
        sql = "SELECT int_version from file where publish_id='{0}'".format(i)
        try:
            res = dbconect(sql)[0]
            temp = (i, res)
            pfxdb_version.append(temp)
        except IndexError:
            pfxdb_version = []
    return pfxdb_version


@app.route('/')
def home():
    '''renders the homepage after successful login'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        # different configs according to dept and access settings
        userLogin = session.get('username')
        # userLogin = 'benjamin'
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        res = get_all(sql)[0]
        print(res)
        session['dept'] = res[0]
        session['access'] = res[1]
        result = get_task_details(userLogin)
        dashbord_dept = [1, 2, 3, 19, 23, 20]

        min_opt = ['YTS', 'WIP', 'HOLD', 'REVIEW']
        low_opt = ['YTS', 'WIP', 'HOLD', 'REVIEW', 'TL_APPROVED', 'TL_IMPROVISE', 'SUP_REVIEW']
        high_opt = ['SUP_REVIEW', 'SUP_APPROVED', 'SUP_IMPROVISE', 'STAGE_1_QC', 'CLIENT_REVIEW']
        max_opt = ['STAGE_1_QC', 'STAGE_1_APPROVED', 'STAGE_1_IMPROVISE', 'STAGE_2_QC', 'CLIENT_REVIEW']
        super_opt = ['STAGE_2_QC', 'STAGE_2_APPROVED', 'STAGE_2_IMPROVISE', 'CLIENT_REVIEW']
        client_opt = ['CLIENT_REVIEW', 'CLIENT_APPROVED', 'CLIENT_IMPROVISE']
        prod_opt = ['YTS', 'WIP', 'HOLD', 'REVIEW', 'CLIENT_REVIEW', 'CLIENT_APPROVED', 'CLIENT_IMPROVISE',
                    'TL_APPROVED', 'TL_IMPROVISE', 'SUP_REVIEW', 'SUP_APPROVED', 'SUP_IMPROVISE', 'STAGE_1_QC',
                    'STAGE_1_APPROVED', 'STAGE_1_IMPROVISE', 'STAGE_2_QC',
                    'STAGE_2_APPROVED', 'STAGE_2_IMPROVISE']

        prod_dept = [11]
        # prod_desn = [32,33,34,36,37,38]
        # status_opt =
        if res[0] in dashbord_dept and res[1] == 'min':
            # print(len(result[0]),len(result[1]),len(result[2]))
            return render_template("dashboard_1.html", username=userLogin, data=result[0], status_opt=min_opt,
                                   versions=result[1], notes=result[2])
        if res[0] in dashbord_dept and res[1] == 'low':
            # print(len(result[0]),len(result[1]),len(result[2]))
            return render_template("TL_dashboard.html", username=userLogin, data=result[0], status_opt=low_opt,
                                   versions=result[1], notes=result[2])
        if res[0] in dashbord_dept and res[1] == 'high':
            # print(len(result[0]),len(result[1]),len(result[2]))
            return render_template("sup_dashboard.html", username=userLogin, data=result[0], status_opt=high_opt,
                                   versions=result[1], notes=result[2])
        if res[0] in dashbord_dept and res[1] == 'max':
            # print(len(result[0]),len(result[1]),len(result[2]))
            return render_template("ravi_dashboard.html", username=userLogin, data=result[0], status_opt=max_opt,
                                   versions=result[1], notes=result[2])
        elif res[0] in prod_dept and res[1] == 'min':
            return render_template("prod_dashbord.html", username=userLogin, data=result[0], status_opt=prod_opt,
                                   versions=result[1], notes=result[2])
        elif res[0] in prod_dept and res[1] == 'low':
            artID = get_artistID(userLogin)
            sql0 = "select proj_code from project_settings"
            overall_proj = dbconect(sql0)
            sql = "select proj_code,thumbnail,category,bid_start_date,bid_end_date,proj_status_id from project_settings " \
                  "where line_producer={0}".format(artID)
            proj_list = get_all(sql)
            sql = "select projcode from tempvariables"
            proj_list2 = get_all(sql)
            projchecklist = []
            for i in overall_proj:
                projchecklist.append(i[0])
            for i in proj_list2:
                projchecklist.append(i[0])
            sql = "select artist_id,login from artist"
            artist_list = get_all(sql)
            user_dict = dict(artist_list)
            return render_template("projects_display.html", u_name=userLogin, proj_list=proj_list, user_list=user_dict,
                                   allprojlist=projchecklist)
        elif res[0] in prod_dept and res[1] == 'high':
            return render_template("pm_dashbord.html", username=userLogin, data=result[0], status_opt=prod_opt,
                                   versions=result[1], notes=result[2])

            # else:
            #     return render_template("artish_dashbord.html", username=userLogin, data=result[0], status_opt=status_opt,
            #                            versions=result[1], notes=result[2])
            # print(len(result[0]), len(result[1]), len(result[2]))
            # print(result[1])
            # print(result[2])
            # return render_template("dashboard_1.html", username=userLogin, data=result[0], status_opt=status_opt,
            #                        versions=result[1], notes=result[2])
            # return render_template("dashboard_1.html", username=userLogin,data=result[0],status_opt=status_opt,versions=result[1])

            # return render_template("dashboard_1.html", username=userLogin,data=result[0],status_opt=status_opt,versions=result[1])


def collect_bidDetails(artistID):
    '''function to collect bid details'''
    sql = "SELECT * from bid_details where created_by={0}".format(artistID)
    res = get_all(sql)
    return res


@app.route('/for_sup_review')
def for_sup_review():
    return render_template("sup_review.html")


@app.route('/my_bids', methods=['GET'])
def myBids():
    '''function to return an LP's bids and it's status'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        return render_template("html_1.html", bid_details=bid_details)


@app.route('/projects', methods=['GET', 'POST'])
def projects():
    '''function to display all projects in DB'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "select proj_code,thumbnail,category,bid_start_date,bid_end_date,proj_status_id from project_settings"
        proj_list = get_all(sql)
        sql = "select projcode from tempvariables"
        proj_list2 = get_all(sql)
        projchecklist = []
        for i in proj_list:
            projchecklist.append(i[0])
        for i in proj_list2:
            projchecklist.append(i[0])
        sql = "select artist_id,login from artist"
        artist_list = get_all(sql)
        user_dict = dict(artist_list)
        return render_template("lp_dashboard.html", u_name=userLogin, proj_list=proj_list, user_list=user_dict,
                               allprojlist=projchecklist)


@app.route('/addProj', methods=['GET'])
def addProj():
    '''function to create new project'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "select proj_code,thumbnail,category,bid_start_date,bid_end_date,proj_status_id from project_settings"
        proj_list = get_all(sql)
        sql = "select projcode from tempvariables"
        proj_list2 = get_all(sql)
        projchecklist = []
        for i in proj_list:
            projchecklist.append(i[0])
        for i in proj_list2:
            projchecklist.append(i[0])
        sql = "select artist_id,login from artist"
        artist_list = get_all(sql)
        user_dict = dict(artist_list)
        return render_template("new_proj.html", u_name=userLogin, proj_list=proj_list, user_list=user_dict,
                               allprojlist=projchecklist)


@app.route('/newBid', methods=['GET', 'POST'])
def newBid():
    '''function to upload new bid excel and then load'''
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        f = request.files['bid_sheet']
        filename = secure_filename(f.filename)
        proj_name = filename.split('_')[0].upper()  # assumed that all project bidding sheets are named as aln_bidding
        bid_folder = UPLOAD_FOLDER + '/' + proj_name
        if not os.path.exists(bid_folder):
            os.mkdir(bid_folder)
        f.save(os.path.join(bid_folder, filename))
        bid_sheet = bid_folder + '/' + filename

        fread_errors = []
        import pandas as pd
        try:
            shot_excel = pd.read_excel(bid_sheet, sheet_name='Shots')
            shot_json = shot_excel.to_json(bid_folder + '/shots.json', orient='records')
            with open(bid_folder + '/shots.json') as f:
                shot_json = json.load(f)



        except:
            shot_json = ''
            fread_errors.append(0)

        try:
            asset_excel = pd.read_excel(bid_sheet, sheet_name='Assets')
            asset_json = asset_excel.to_json(bid_folder + '/assets.json', orient='records')
            with open(bid_folder + '/assets.json') as f:
                asset_json = json.load(f)

        except:
            asset_json = ''
            fread_errors.append(1)
            asset_headers = []
        headers = ['CONPT', 'ANI', 'MGS', 'MAT', 'MM', 'ROT', 'RA', 'DYN', 'LIT', 'REN', 'PRE COMP', 'PNT', 'COM',
                   'STORYBOARD', 'MOD', 'TEX', 'UV', 'FUR', 'RIG', 'LOOKDEV']
        sql = "select login from artist"
        artist_list = get_all(sql)
        user_list = []
        for j in artist_list:
            user_list.append(j[0])
        print(user_list)
        return render_template("bid_table.html", proj=proj_name, errors=fread_errors, shot_json=shot_json,
                               asset_json=asset_json, keys=headers, user_list=user_list)


def get_login(artistID):
    '''function to get login given artist ID'''
    sql = "SELECT login from artist where artist_id={0}".format(artistID)
    try:
        res = dbconect(sql)[0]
    except IndexError:
        res = ''
    return res


@app.route('/<proj_code>/editProj')
def editProj(proj_code):
    '''editing project'''
    # if request.method == 'POST':
    #     data = request.get_json()
    #     proj_code = data['result']
    #     print(proj_code,'proj_code')
    #     return '',200
    # elif request.method == 'GET':
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        import os
        userLogin = session.get('username')
        sql = "SELECT * from project_settings where proj_code='{0}'".format(proj_code)
        res = get_all(sql)[0]
        lp = get_login(res[12])  # get artist login given their artist ID
        print(lp)
        coord_3d = get_login(res[13])
        coord_2d = get_login(res[14])
        proj_manager = get_login(res[15])
        vfx_head = get_login(res[16])
        vfx_sup = get_login(res[17])
        head_2d = get_login(res[18])
        art_dir = get_login(res[19])
        cg_sup = get_login(res[20])
        roto_coord = get_login(res[21])
        paint_coord = get_login(res[22])
        roto_sup = get_login(res[23])
        paint_sup = get_login(res[24])
        stat = res[26]
        if type(stat) == int:
            sql = "SELECT status_name from project_status where project_status_id={0}".format(stat)
            stat - dbconect(sql)[0]
        else:
            pass

        proj_details = dict(code=proj_code, thumbnail=os.path.basename(res[2]), resolution=res[3], category=res[4],
                            fps=res[5], inpDate=res[6], outDate=res[7], slate_2d=res[8],
                            slate_3d=res[9], macro_2d=res[10], macro_3d=res[11], lp=lp, cord_2d=coord_2d,
                            cord_3d=coord_3d, pm=proj_manager, head=vfx_head, sup=vfx_sup, head2d=head_2d,
                            artdir=art_dir, cgsup=cg_sup, roto=roto_coord, pnt=paint_coord, rotosup=roto_sup,
                            pntsup=paint_sup, ocio=res[25], status=stat, bid_st=res[27],
                            bid_e=res[28], inp=res[33], out=res[34], qt_codec=res[35], qt_res=res[36], tech_doc=res[37])

        return render_template("edit_proj.html", details=proj_details,
                               projCategory=['VFX', 'ROTO', 'PAINT', 'PREP', '2D', '3D'],
                               projStatus=['IN_PROGRESS', 'YTS', 'WIP', 'PAUSE', 'HOLD', 'REMOVED', 'DELIVERED'])


@app.route('/login', methods=['POST'])
def do_admin_login():
    sql = "SELECT password,salt from artist where login = '{0}'".format(request.form['username'])
    try:
        paswd = get_all(sql)[0]
        key_select = paswd[1].encode()
        encripted = paswd[0].encode()
        f = Fernet(key_select)
        password = f.decrypt(encripted)
        # print(password)
        if request.form['password'] == password.decode():
            session['logged_in'] = True
            session['username'] = request.form['username']
            return home()
        else:
            flash('wrong password!')
            return home()
    except:
        flash('Wrong Username!')
        return home()


def get_artist_notes(artistName):
    '''function to get all notes given to an artist'''
    sql = "SELECT proj_name,scope_name,type_name,int_version,reviewer_name,notes,attachment from notes where artist_name='{0}'".format(
        artistName)
    res = get_all(sql)
    return res


def get_artist_project(artistName):
    '''function to get all project name assign to an artist'''
    sql = "SELECT artist_id from artist where login='{0}'".format(artistName)
    art_id = get_all(sql)[0][0]
    sql = "SELECT DISTINCT proj_id from task where assigned_to='{0}'".format(
        art_id)
    proj_id = get_all(sql)
    list1 = []
    for i in proj_id:
        sql = "SELECT proj_code from project_settings where proj_id ='{0}'".format(i[0])
        list1.append(dbconect(sql)[0])
    return list1


def get_artist_task(artistName):
    sql = "SELECT artist_id from artist where login='{0}'".format(artistName)
    art_id = get_all(sql)[0][0]
    sql = "SELECT DISTINCT task_type_name from task where assigned_to='{0}'".format(
        art_id)
    list1 = get_all(sql)
    task_nam = []
    for i in list1:
        task_nam.append(i[0])
    return task_nam


def get_task_type():
    sql = "SELECT DISTINCT task_type_name from task_type"
    list1 = get_all(sql)
    list1 = get_all(sql)
    task_nam = []
    for i in list1:
        task_nam.append(i[0])
    return task_nam


@app.route("/notes")
def notes():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        userLogin = session.get('username')
        temp = get_artist_notes(userLogin)
        retList = []
        notes = []
        for j in temp:
            k = dict(proj=j[0], scope=j[1], type=j[2], int_version=j[3], reviewer=j[4], notes=j[5], attachment=j[6])
            notes.append(k)
        retList.append(notes)
        # print(notes)
        temp = get_artist_project(userLogin)
        retList.append(temp)
        # print(temp)
        temp = get_task_type()
        # print(temp)
        retList.append(temp)
        # print(retList)
    # return str(retList)
    return render_template("test.html", user=retList)


@app.route("/note",methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        data = request.get_json()
        print('Hello1')
        print(data)
        print(data['pNames'])
        print(data['tNames'])
        userLogin = session.get('username')
        temp = get_artist_notes(userLogin)
        retList = []
        notes = []
        type_convert = {'ROT': '2d_roto', '2D_ELEMENT': '2d_element', 'PAINT': '2d_paint', 'MATTEPAINT': 'art_mattepaint',
                'CONCEPT_ART': 'concept_art', '2D_LAYOUT': '2d_layout', 'SLAPCOMP': '2d_slapcomp',
                'PRECOMP': '2d_precomp', 'COMP': '2d_out', '2D_TEST': '2d_test', 'MATCHMOVE': '3d_matchmove',
                'MODEL': '3d_model', 'HDRI': '3d_hdri', 'RIGGING': '3d_rigging', 'SHADING': '3d_shading',
                'LOOKDEV': '3d_lookdev', '3D_TEST': '3d_test', 'LIGHTING': '3d_lighting', 'DYNAMICS': '3d_dynamics',
                'SHOTSCULPT': '3d_shotsculpt', '3D_ANIMATION': '3d_animation', 'TEXTURING': '3d_texture',
                'PREVIZ': 'pre_visualisation', 'PIPE_TEST': 'pipe_test', 'PIPE_OUT': 'pipe_out',
                '3D_LAYOUT': '3d_layout'}
        for j in temp:
            convertion_list = []
            for i in data['tNames']:
                print(i)
                convertion_list.append(type_convert[i])
            print('CL: ', convertion_list)
            if j[0] in data['pNames'] and j[2] in convertion_list:
                k = dict(proj=j[0], scope=j[1], type=j[2], int_version=j[3], reviewer=j[4], notes=j[5], attachment=j[6])
                notes.append(k)
        retList.append(notes)
        temp = get_artist_project(userLogin)
        retList.append(temp)
        temp = get_task_type()
        retList.append(temp)
        print(retList)
        return jsonify(user=retList)
        # return '',200


@app.route("/shot", methods=['GET', 'POST'])
def shot():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        userLogin = session.get('username')
        sql = "select proj_id,thumbnail,scope_category_id,scope_name,scope_description,SAP,production_status,scope_id from scope where proj_id=70"
        proj_list = get_lcl(sql)
        proj_dict = []
        for j in proj_list:
            detail = j[3].rsplit('/', 1)
            name = detail[1]
            category = detail[0]
            k = dict(proj_id=j[0], thumnail=j[1], category=category, name=name, description=j[4], SAP=j[5], status=j[6], scope_id=j[7])
            proj_dict.append(k)
        sql2 = "SELECT scope_id,task_type_name,assigned_to,EMD,CMD,task_status,latest_int_version,latest_client_version,bid_end FROM `task` WHERE proj_id=70 "
        task_list = get_lcl(sql2)
        task_dict = []
        for j in task_list:
            k = dict(scope_id=j[0], task=j[1], assigned=j[2], emd=j[3], cmd=j[4], status=j[5], intversion=j[6], clientversion=j[7], due=j[8])
            task_dict.append(k)
        l = len(task_dict)
        sql3 = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid=70 "
        scope_list = get_lcl(sql3)
        scope_dict = []
        for j in scope_list:
            k = dict(c_id=j[0], c_name=j[1], sc_id=j[2])
            scope_dict.append(k)
        return render_template ("shot.html", proj_dict=proj_dict, task_dict=task_dict, scope_dict=scope_dict,l=l)
@app.route("/modal", methods=['POST'])
def modal():
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        taskID = get_task_id(result['project'], result['scope'], result['task'], result['artist'])
        pubID = get_publish_id(taskID)
        print(pubID, taskID)
        version_dict = get_pfxdb_version(pubID)
        return jsonify(versions=version_dict)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route("/setting")
def setting():
    if not session.get('logged_in'):
        return home()
    else:
        username = session.get('username')
        return render_template("setting.html", result=username)


@app.route("/changPasword", methods=['POST'])
def changPasword():
    if not session.get('logged_in'):
        return home()
    else:
        username = session.get('username')
        sql = "SELECT password,salt from artist where login = '{0}'".format(username)
        try:
            paswd = get_all(sql)[0]
            key_select = paswd[1].encode()
            encripted = paswd[0].encode()
            f = Fernet(key_select)
            password = f.decrypt(encripted)
            if request.form['currentpwd'] == password.decode():
                if request.form['newpwd'] == request.form['retyppwd']:
                    password_provided = request.form['newpwd'].encode()
                    key = Fernet.generate_key()
                    f = Fernet(key)
                    token = f.encrypt(password_provided)
                    salt = key.decode()
                    passcode = token.decode()
                    try:
                        # print(passcode, salt, username)
                        sql = "UPDATE `artist` SET `password`= '{0}',`salt`='{1}' WHERE `login` = '{2}'".format(
                            passcode, salt, username)
                        paswd = dbconect(sql)
                        flash('Update Successfully!')
                        return setting()
                    except:
                        flash('Error in Update!')
                        return setting()
                else:
                    flash('Password Mismatch!')
                    return setting()
            else:
                flash('Wrong Password!')
                return setting()
        except:
            flash('Wrong Username!')
            return changPasword()


def get_task_typeID(task_name):
    '''getting task type ID if task name is given'''
    sql = "SELECT task_status_id from task_status where task_status_name = '{0}'".format(task_name.upper())
    res = dbconect(sql)[0]
    return res


def update_status(task_id, task_status):
    '''updating task_id status'''
    taskIypeID = get_task_typeID(task_status)
    sql = "UPDATE task SET task_status={0} WHERE task_id={1}".format(taskIypeID, task_id)
    try:
        res = dbconect(sql)
        return True
    except:
        return False


def check_workHour(task_id):
    '''checth last calculated work hour of the project'''

    sql = "SELECT work_hours from task_work_hrs where task_id={0}".format(task_id)
    res = dbconect(sql)
    current_stamp = datetime.now()  # get current timestamp
    if res == []:
        sql = "INSERT into task_work_hrs(task_id,start_time,processed_time) VALUES({0},'{1}','{2}')".format(task_id,
                                                                                                            current_stamp,
                                                                                                            current_stamp)
        res1 = dbconect(sql)
        res = "00:00:00"
    else:
        pass
    return res[0]


def get_workHour(task_id):
    '''checth last calculated work hour of the project'''
    sql = "SELECT work_hours from task_work_hrs where task_id={0}".format(task_id)
    res = dbconect(sql)
    current_stamp = datetime.now()  # get current timestamp
    if res == []:
        res = ("00:00:00", '0')
    else:
        sql = "SELECT processed_time from task_work_hrs where task_id={0}".format(task_id)
        res1 = dbconect(sql)
        res = (res[0], res1[0])
    return res


@app.route("/pause_calc", methods=['POST'])
def pause_calc():
    '''end point to post if person clicks meeting or break'''
    from datetime import datetime
    data = request.get_json()
    result = data['result']
    task_id = result['task_id']
    status = result['opt']
    update_status(int(task_id), status)
    if status == 'PAUSE':
        curr_time = datetime.now()
        sql = "UPDATE task_work_hrs SET stop_time='{0}' where task_id='{1}'".format(curr_time, task_id)
        res = dbconect(sql)
        sql1 = "SELECT stop_time,processed_time from task_work_hrs where task_id='{0}'".format(task_id)
        res = get_all(sql1)[0]
        duration = (res[0] - res[1]).total_seconds()
        temp = check_workHour(task_id)
        if temp != "00:00:00":
            h, m, s = temp.split(":")
            time = int(h) * 3600 + int(m) * 60 + int(s)
        else:
            time = 0

        overall = time + duration
        mins = divmod(overall, 60)
        hrs = divmod(mins[0], 60)
        print('check')
        work_hrs = str(int(hrs[0])) + ':' + str(int(hrs[1])) + ':' + str(int(mins[1]))
        sql2 = "UPDATE task_work_hrs SET work_hours='{0}' where task_id='{1}'".format(work_hrs, task_id)
        res = dbconect(sql2)

    elif status == 'WIP':
        curr_time = datetime.now()

        sql = "UPDATE task_work_hrs SET processed_time='{0}' where task_id='{1}'".format(curr_time, task_id)
        res = dbconect(sql)
    return '', 200


@app.route("/status_change", methods=['POST'])
def status_change():
    '''end point to post changes'''
    if request.method == 'POST':

        data = request.get_json()
        result = data['result']
        task_id = result['task_id']
        status = result['opt']
        count_statuses = ['WIP']
        stop_statuses = ['PAUSE', 'HOLD', 'REVIEW']

        if status.upper() in count_statuses:
            curr_time = datetime.now()
            sql = "UPDATE task_work_hrs SET processed_time='{0}' where task_id='{1}'".format(curr_time, task_id)
            res = dbconect(sql)

        elif status.upper() in stop_statuses:
            curr_time = datetime.now()
            sql = "UPDATE task_work_hrs SET stop_time='{0}' where task_id='{1}'".format(curr_time, task_id)
            res = dbconect(sql)
            sql1 = "SELECT stop_time,processed_time from task_work_hrs where task_id='{0}'".format(task_id)
            res = get_all(sql1)[0]
            duration = (res[0] - res[1]).total_seconds()
            temp = check_workHour(task_id)
            if temp != "00:00:00":
                h, m, s = temp.split(":")
                time = int(h) * 3600 + int(m) * 60 + int(s)
            else:
                time = 0

            overall = time + duration
            mins = divmod(overall, 60)
            hrs = divmod(mins[0], 60)
            work_hrs = str(int(hrs[0])) + ':' + str(int(hrs[1])) + ':' + str(int(mins[1]))
            sql2 = "UPDATE task_work_hrs SET work_hours='{0}' where task_id='{1}'".format(work_hrs, task_id)
            res = dbconect(sql2)

        workHourCheck = check_workHour(task_id)
        time = workHourCheck.split(':')
        success = update_status(task_id, status)
        # print(result,time)
        return jsonify(time=time)


@app.route("/timer", methods=['POST'])
def timer_display():
    '''end point to get work hours to display'''
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        task_id = result['task_id']
        # print(result)
        # return jsonify(success=success)
        workHourCheck = check_workHour(task_id)
        time = workHourCheck.split(':')
        return jsonify(time=time)


@app.route("/stopwatch", methods=['POST'])
def stopwatch():
    '''end point to post changes'''
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        task_id = result['task_id']
        status = result['opt']
        workHourCheck = get_workHour(task_id)
        time = workHourCheck[0].split(':')
        if workHourCheck[1] != '0':
            print(workHourCheck[1])
            current_stamp = datetime.now()
            print(current_stamp)
            tdelta = current_stamp - workHourCheck[1]
            print(workHourCheck[0])
            inSecs = get_sec(workHourCheck[0])
            print('WH', inSecs)
            seconds = tdelta.days * 24 * 3600 + tdelta.seconds
            print(seconds)
            total = int(inSecs) + int(seconds)
            print(total)
        else:
            total = 0
        print(result, time)
        return jsonify(time=time, seconds=total)


def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


@app.route("/nproj")
def newProject():
    if not session.get('logged_in'):
        return home()
    elif session['logged_in'] == False:
        return home()
    else:
        username = session.get('username')
        form = MyForm()
        return render_template("projnew.html", form=form)


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")


def validate_status(username):
    # return 0 if task is in WIP and 1 if no tasks are in WIP
    artID = get_artistID(username)
    sql = "SELECT task_id from task where assigned_to = {0} and task_status=19".format(artID)
    res = dbconect(sql)
    print(res)
    if res != []:
        return 0
    else:
        return 1


@app.route("/validate", methods=['POST'])
def validate():
    '''don't logout if there are tasks in WIP'''
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        success = validate_status(result)
        return jsonify(success=success)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run('0.0.0.0', 80, debug=True)
