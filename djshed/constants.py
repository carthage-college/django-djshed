# -*- coding: utf-8 -*-

SCHEDULE_SQL = '''
    SELECT
        sec_rec.hrs,
        sec_rec.subsess,
        TRIM(sec_rec.title) as title,
        sec_rec.max_reg,
        sec_rec.reg_num,
        sec_rec.fac_id sec_fac_id,
        fac_rec.abbr_name sec_fac_abbr_name,
        TRIM(sec_rec.crs_no) as crs_no,
        sec_rec.cat,
        sec_rec.yr,
        sec_rec.sess,
        sec_rec.sess[1,1] program, --only used for alphabetical listing
        sec_rec.sec_no,
        sec_rec.ref_no,
        crs_rec.dept,
        TRIM(crs_rec.title1) as title1,
        TRIM(crs_rec.title2) as title2,
        TRIM(crs_rec.title3) as title3,
        mtg_rec.beg_tm,
        mtg_rec.end_tm,
        mtg_rec.mtg_no,
        mtg_rec.days,
        mtg_rec.bldg,
        mtg_rec.room,
        (dept_table.txt) dept_text
    FROM
        sec_rec,
        crs_rec,
        dept_table,
        div_table,
        acad_cal_rec,
        id_rec,
        outer (secmtg_rec, outer mtg_rec),
        outer fac_rec
    WHERE
        sec_rec.fac_id = id_rec.id
        AND  sec_rec.fac_id = fac_rec.id
        AND  sec_rec.crs_no = crs_rec.crs_no
        AND  sec_rec.cat = crs_rec.cat
        AND  sec_rec.crs_no = secmtg_rec.crs_no
        AND  sec_rec.cat = secmtg_rec.cat
        AND  sec_rec.yr = secmtg_rec.yr
        AND  sec_rec.sess = secmtg_rec.sess
        AND  sec_rec.sec_no = secmtg_rec.sec_no
        AND  secmtg_rec.mtg_no = mtg_rec.mtg_no
        AND  sec_rec.stat NOT IN ("X", "I")
        AND  crs_rec.dept = dept_table.dept
        AND  dept_table.div = div_table.div
        AND  acad_cal_rec.prog = crs_rec.prog
        AND  acad_cal_rec.sess = sec_rec.sess
        AND  acad_cal_rec.subsess = sec_rec.subsess
        AND  acad_cal_rec.yr = sec_rec.yr
        AND  sec_rec.print_schd <> "N"
        AND  sec_rec.stat <> "SEC_STAT_CANCEL"
        AND  mtg_rec.schd_print <> "N"
        {where}
        AND  NVL(mtg_rec.beg_tm, 0) != 0
        AND  NVL(mtg_rec.end_tm, 0) != 0
'''.format

DATES = '''
    SELECT
        beg_date, end_date, last_add_date, last_drop_date,
        last_wd_date, subsess
    FROM
        acad_cal_rec
'''
