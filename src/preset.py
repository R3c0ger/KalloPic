#!usr/bin/env python
# -*- coding: utf-8 -*-

# 匹配优先级：\{(.+(\n.+){2,6}\])},
# 建议搭配“选择所有匹配项”和String Manipulation插件进行修改

DIR_KEYWORD_MAP = {
    "博丽灵梦": [
        0,  # 出场次数优先级，越小越靠前
        "boli", "lingmeng", "bllm", "bl", "lm",  # 中文拼音：姓、名、姓名首字母、姓首字母、名首字母
        "hakurei", "reimu",  # 罗马音：姓、名
        "hb", "hongbai", "wunv", "wn", "miko", "rim", "ywn", "swwn", "chengguan", "cg", "cssrm",  # 昵称、相关外号
        "zhujue", "zj", "yuandian", "yd", "jiejie", "jj",  # cp
    ],
    "雾雨魔理沙": [
        1,
        "wuyu", "molisha", "wymls", "wy", "mls",
        "kirisame", "marisa",
        "hb", "heibai", "witch", "mrs", "ss", "shasha", "yongchang", "yc", "mns", "jfxnh", "mpz", "shasha",
        "tk", "zhujue", "zj",
    ],
    "十六夜咲夜": [
        2,
        "shiliuye", "xiaoye", "slyxy", "sly", "xy",
        "izayoi", "sakuya",
        "pad", "padz", "maid", "dio", "world", "sky", "np", "xyy",
        "meixiao", "mx",
    ],
    "魂魄妖梦": [
        3,
        "hunpo", "yaomeng", "hpym", "hp", "ym",
        "konpaku", "youmu",
        "yomeng", "yo", "mashu", "umeng", "um", "myon", "yooooo", "qljs",
        "youming",
    ],
    "八云紫": [
        4,
        "bayunzi", "bayun", "zi", "byz", "by", "z",
        "yukari", "yakumo",
        "bba", "zima", "zimei", "zm", "ltp", "ykl", "shiqi", "sq",
        "qiannian", "qn", "jiejie", "jj",
    ],
    "蕾米莉亚": [
        5,
        "leimiliya", "sikaleite", "lmlysklt", "lmly", "sklt",
        "remilia", "scarlet",
        "daxiaojie", "dxj", "leimi", "lm", "xxg", "weiyan", "sister", "btdf",
        "jiejie", "jj", "jiemei", "beide", "bd",
    ],
    "西行寺幽幽子": [
        6,
        "xixingsi", "youyouzi", "xxsyyz", "xxs", "yyz",
        "saigyouji", "yuyuko", "sgj", "yyk",
        "uuz", "chihuo", "dww", "yy",
        "qn", "qiannian", "ym", "youming",
    ],
    "射命丸文": [
        7,
        "shemingwan", "wen", "smww", "smw", "w",
        "aya", "wenwen", "ww", "xgjz", "gzw", "ayayaya",
        "wenhua", "wh",
    ],
    "琪露诺": [
        8,
        "qilunuo", "qln", "q",
        "cirno", "chiruno",
        "baka", "bendan", "jiu", "xj", "nine", "yousei", "yaojing",
        "yjz", "yj",
    ],
    "八云蓝": [
        9,
        "bayunlan", "byl", "by", "l",
        "yakumo", "ran",
        "slth", "lanma", "lm", "hl", "huli", "jwh",
    ],
    "伊吹萃香": [
        10,
        "yichui", "cuixiang", "yccx", "yc", "cx",
        "ibuki", "suika",
        "melon", "xigua", "xg", "oni", "gui", "glls", "gm", "zx", "sik",
    ],
    "东风谷早苗": [
        11,
        "dongfenggu", "zaomiao", "dfgzm", "dfg", "zm",
        "kochiya", "kotiya", "sanae",
        "m", "miaoye", "my", "miko", "fengzhu", "fz", "she", "caotian", "ct", "xrs", "mm", "jdxzm",
        "wunv", "wn",
    ],
    "八坂神奈子": [
        12,
        "baban", "shennaizi", "bbsnz", "bb", "snz",
        "yasaka", "kanako",
        "shenma", "sm", "yuzhu", "ss", "fs", "feishen", "bba", "mj",
    ],
    "帕秋莉": [
        13,
        "paqiuli", "nuoleiji", "pqlnlj", "pql", "nlj",
        "patchouli", "knowledge",
        "muq", "mq", "paqi", "pq", "ghx",
    ],
    "橙": [
        14,
        "cheng", "ch", "c", "chen",
        "bayun", "by", "chengmiao", "cm", "cheeeeeeeeen",
    ],
    "爱丽丝": [
        15,
        "ailisi", "mageteluoyide", "als", "mgtlyd", "am",
        "alice", "margatroid",
        "mls", "mrs", "weizhentian", "wzt", "xiaoai", "xa", "renou", "ro",
        "yongchang", "yc",
    ],
    "铃仙": [
        16,
        "lingxian", "youtanhuayuan", "youtanhua", "yinfan", "lx", "ythy", "yth", "yf", "lyy",
        "reisen", "udongein", "inaba", "rs",
        "wudong", "udon", "wd", "tutu", "shoutu", "st", "yzlb", "zyt",
    ],
    "洩矢诹访子": [
        17,
        "xieshi", "zoufangzi", "xszfz", "zfz",
        "moriya", "suwako", "swk",
        "qingwazi", "qingwa", "qwz", "qw", "mo", "xym", "zf",
        "feishen", "fs",
    ],
    "八意永琳": [
        18,
        "bayi", "yonglin", "byyl", "by", "yl",
        "eirin", "yagokoro", "er",
        "tasuke", "helpme", "tsk", "shijiang", "pzj", "yztn", "jsc", "bba",
        "yongyuan", "yy",
    ],
    "藤原妹红": [
        19,
        "tengyuan", "meihong", "tymh", "ty", "mh",
        "Huziwara", "Mokou", "hzwr", "mk",
        "yemen", "ymh", "mokotan", "mogutan", "mgt", "bsn",
        "busi", "bsz", "bs", "zhulin", "zl",
    ],
    "河城荷取": [
        20,
        "hecheng", "hequ", 'hchq', "hc", "hq"
        'kawasiro", "nitori',
        "hetong", "ht", "huanggua", "hg", "htzg", "lbn",
    ],
    "因幡帝": [
        21,
        "yinfan", "di", "tianwei", "yfd", "yftw", "yf", "d", "tw",
        "tewi", "inaba",
        "didi", "fuheitu", "fuhei", "xld", "fh", "htz", "tutu",
    ],
    "莉莉霍瓦特": [
        22,
        "lili", "huowate", "llhwt", "hwt",
        "lilywhite", "lily", "white",
        "lilibai", "lilihei", "llb", "b", "llh", "bll", "czyj", "jcj",
    ],
    "蓬莱山辉夜": [
        23,
        "penglaishan", "huiye", "plshy", "pls", "hy",
        "houraisan", "kaguya",
        "neet", "hyj",
        "bs", "busi", "bsz", "yongyuan", "yy",
    ],
    "小野塚小町": [
        24,
        "xiaoyezhong", "xiaoting", "xyzxt", "xyz", "xt",
        "onozuka", "onoduka", "komachi",
        "sishen", "ss", "ruting", "rt",
    ],
    "比那名居天子": [
        25,
        "binamingju", "tianzi", "bnmtz", "bn", "tz",
        "hinanawi", "tenshi",
        "tln", "mz", "mzi", "momoko", "mmk", "taozi",
    ],
    "圣白莲": [
        26,
        "sheng", "bailian", "sbl", "s", "bl",
        "hiziri", "hijiri", "byakuren",
        "lianma", "lm", "sjdhmz", "mfs", "motor", "mt", "mls", "bba",
    ],
    "云居一轮": [
        27,
        "yunju", "yilun", "yjyl", "yj", "yl",
        "kumoi", "ichirin",
        "unzan", "ys",
    ],
    "二岩猯藏": [
        28,
        "eryan", "tuanzang", "eytz", "ey", "tz",
        "hutatsuiwa", "futatsuiwa", "mamizou",
        "dalizi", "dlz", "ruizang", "rz", "limao",
    ],
    "上白泽慧音": [
        29,
        "shangbaize", "huiyin", "sbzhy", "sbz", "hy",
        "kamishirasawa", "keine",
        "laoshi", "ls", "xbzhy", "baize", "bz",
        "zhulin", "zl",
    ],
    "丰聪耳神子": [
        30,
        "fengconger", "shenzi", "fcesz", "fce", "sz",
        "toyosatomimi", "miko", "tnm",
        "taizi", "tz", "sdtz", "esz", "bba",
    ],
    "宇佐见莲子": [
        31,
        "yuzuojian", "lianzi", "yzjlz", "yzj", "lz",
        "usami", "renko",
        "mifeng", "mf", "dxs",
    ],
    "玛艾露贝莉·赫恩": [
        32,
        "maailubeili", "heen", "malblhe", "malbl",
        "maribel", "hearn",
        "meili", "ml", "mifeng", "mf", "dxs", "byz",
    ],
    "红美铃": [
        33,
        "hong", "meiling", "hml", "h", "ml",
        "hon", "meirin",
        "hsf",  "zhongguo", "zg", "mw",
        "sjmxjc", "meixiao", "mx",
    ],
    "米斯蒂娅·萝蕾拉": [
        34,
        "misidiya", "luoleila", "msdylll", "msdy", "lll", "msd",
        "mystia", "lorelei",
        "lbn", "xcg", "cuigu", "msq", "nsjy", "bksyn", "yq", "yeque",
    ],
    "秋穰子": [
        35,
        "qiu", "rangzi", "qrz", "q", "rz",
        "aki", "minoriko",
        "hongshu", "qjm", "mm", "qxz", "xz",
    ],
    "火焰猫燐": [
        36,
        "huoyanmao", "lin", "hyml", "hym", "l",
        "kaenbyou", "rin",
        "alin", "al", "maoche", "mc", "hc",
        "chongwu", "cwz", "cw",
    ],
    "灵乌路空": [
        37,
        "lingwulu", "kong", "lwlk", "lwl", "k",
        "reiuji", "utsuho",
        "akong", "ak", "gaoda", "gd", "hedan", "hd", "h", "six", "liu", "wuya", "wy",
        "chongwu", "cwz", "cw",
    ],
    "古明地恋": [
        38,
        "gumingdi", "lian", "gmld", "gmd", "l",
        "komeiji", "koishi",
        "lianlian", "ll", "xiaoshi", "xst", "gmdsx", "wuyisi", "wys", "dmx", "tezg", "mzxs",
        "meimei", "mm", "juelian", "jl", "ddjm",
    ],
    "多多良小伞": [
        39,
        "duoduoliang", "xiaosan", "ddlxs", "ddl", "xs",
        "tatara", "kogasa",
        "xsj", "tangsan", "ts", "tsyg",
    ],
    "斯塔萨菲雅": [
        40,
        "sita", "safeiya", "stsfy", "st", "sfy",
        "star", "sapphire",
        "syj", "yj",
    ],
    "桑尼米尔克": [
        41,
        "sangni", "mierke", "snmek", "sn", "mek",
        "sunny", "milk",
        "syj", "yj", "gmnn",
    ],
    "露娜切露德": [
        42,
        "luna", "qielude", "lnqld", "ln", "qld",
        "child",
        "syj", "yj", "lnc",
    ],
    "四季映姬": [
        43,
        "sijiyingji", "yemoxiannadu", "sjyj", "siji", "sj", "yingji", "yj", "ymxnd", "ymsnd",
        "shikieiki", "yamaxanadu", "shiki", "eiki",
        "ylw", "yanluo", "yl", "sjdr", "snt",
    ],
    "秋静叶": [
        44,
        "qiu", "jingye", "qjy", "q", "jy",
        "aki", "sizuha",
        "jiejie", "jj", "qjm", "qj",
    ],
    "键山雏": [
        45,
        "jianshan", "chu", "jsc", "js", "c",
        "kagiyama", "hina",
        "zhuanzhuan", "zhuan", "zz", "eshen", "es", "xln", "srn",
    ],
    "星熊勇仪": [
        46,
        "xingxiong", "yongyi", "xxyy", "xx", "yy",
        "hoshiguma", "yuugi",
        "hys", "oni", "gui",
    ],
    "古明地觉": [
        47,
        "gumingdi", "jue", "gmdj", "gmd", "j",
        "komeiji", "satori",
        "xiaowu", "wu", "five", "xwu", "xwll",
        "jiejie", "jj", "juelian", "jl", "ddjm",
    ],
    "娜兹玲": [
        48,
        "naziling", "nzl", "ncl",
        "nazrin", "n",
        "laoshu", "ls", "xb",
    ],
    "芙兰朵露": [
        49,
        "fulanduolu", "sikaleite", "fldl", "sklt",
        "flandre", "scarlet", "fs",
        "erxiaojie", "exj", "ermei", "em", "fulan", "fl", "lll", "xhscjd", "xxg",
        "meimei", "mm", "beide", "bd",
    ],
    "蕾蒂": [
        50,
        "leidi", "huowateluoke", "ldhwtlk", "ld", "hwtlk",
        "letty", "whiterock",
        "jiuma", "heimu", "xn",
    ],
    "莉格露": [
        51,
        "ligelu", "naitebage", "lgl", "ntbg",
        "wriggle", "nightbug",
        "bug", "chongzi", "cz",
    ],
    "黑谷山女": [
        52,
        "heigu", "shannv", "hgsn", "hg", "sn",
        "kurodani", "yamame",
        "zhizhu", "spider", "zz", "tzz",
    ],
    "村纱水蜜": [
        53,
        "cunsha", "shuimi", "cssm", "cs", "sm",
        "murasa", "minamitsu",
        "captain", "chuanzhang", "cz", "cyl",
    ],
    "寅丸星": [
        54,
        "yinwan", "xing", "ywx", "yw", "x",
        "toramaru", "shou",
        "dsx", "laohu", "lh", "dasheng", "ds", "swk", "wk",
    ],
    "封兽鵺": [
        55,
        "fengshou", "ye", "fsy", "fs", "y",
        "houjuu", "nue",
        "alien", "wxr", "jml", "qml", "yejiang", "yj", "hy", "cs",
    ],
    "姬海棠果": [
        56,
        "jihaitang", "guo", "jhtg", "jht", "g",
        "himekaidou", "hatate",
        "gg", "guoguo", "jizhe",
    ],
    "幽谷响子": [
        57,
        "yougu", "xiangzi", "ygxz", "yg", "xz",
        "kasodani", "kyouko",
        "fdj", "sy", "yahoo", "nsjy",
    ],
    "物部布都": [
        58,
        "wubu", "budu", "wbbd", "wb", "bd",
        "mononobe", "futo", "mf", "mnf",
        "bududu", "bdd", "fuhei", "fh", "mt",
    ],
    "露米娅": [
        59,
        "lumiya", "lmy",
        "rumia", "r",
        "shi", "ten", "baka", "sjz", "t",
    ],
    "莉莉卡·普莉兹姆利巴": [
        60,
        "lilika", "pulizimuliba", "llk", "plzmlb",
        "lyrica", "prismriver", "lp",
        "ljh", "slsjm", "sl", "jp",
    ],
    "露娜萨·普莉兹姆利巴": [
        61,
        "lunasa", "pulizimuliba", "lns", "plzmlb",
        "lunasa", "prismriver", "lp",
        "ljh", "slsjm", "sl", "xtq", "tq",
    ],
    "梅露兰·普莉兹姆利巴": [
        62,
        "meilulan", "pulizimuliba", "mll", "plzmlb",
        "merlin", "prismriver",
        "ljh", "slsjm", "sl", "xiaohao", "xh",
    ],
    "永江衣玖": [
        63,
        "yongjiang", "yijiu", "yjyj", "yj",
        "nagae", "iku",
        "lgsz", "hdy", "zsd", "dianman", "dm",
    ],
    "少名针妙丸": [
        64,
        "shaoming", "zhenmiaowan", "smzmw", "sm", "zmw",
        "sukuna", "shinmyoumaru",
        "xiaowan", "xw", "xgz", "ycfs", "ycl",
    ],
    "宇佐见堇子": [
        65,
        "yuzuojian", "jinzi", "yzjjz", "yzj", "jz",
        "usami", "sumireko",
        "jk", "gzs", "mf", "mifeng",
    ],
    "风见幽香": [
        66,
        "fengjian", "youxiang", "fj", "yx", "fjyx",
        "kazami", "yuuka",
        "huama", "hm", "hthf", "htcf", "hzbj",
    ],
    "犬走椛": [
        67,
        "quanzou", "hua", "qz", "h", "qzh",
        "inubashiri", "momiji",
        "momiji", "mmj", "gougou", "gg", "xbg", "xbl", "huahua", "hh",
    ],
    "水桥帕露西": [
        68,
        "shuiqiao", "paluxi", "sqplx", "sq", "plx",
        "mizuhashi", "parsee",
        "qiaoji", "qj", "jidu", "palu", "pl",
    ],
    "赤蛮奇": [
        69,
        "chi", "manqi", "cmq", "c", "mq",
        "sekibanki", "skbk", "banki",
        "ftm", "seven", "qi", "qy", "cmt", "cj",
    ],
    "堀川雷鼓": [
        70,
        "kuchuan", "leigu", "kclg", "kc", "lg",
        "horikawa", "raiko",
        "guge", "gg",
    ],
    "茨木华扇": [
        71,
        "cimu", "huashan", "cmhs", "cm", "hs",
        "ibaraki", "kasen",
        "xianren", "xr", "cmtz", "hso", "chx", "baozi", "bz", "bzx",
    ],
    "宫古芳香": [
        72,
        "gonggu", "fangxiang", "ggfx", "gg", "fx",
        "miyako", "yoshika",
        "zombie", "js",
    ],
    "霍青娥": [
        73,
        "huo", "qinge", "h", "qe", "hqe",
        "kaku", "seiga",
        "qenn", "nn", "xr", "sj", "shijia",
    ],
    "苏我屠自古": [
        74,
        "suwo", "tuzigu", "swtzg", "sw", "tzg",
        "soga", "tojiko",
        "dagen", "dg", "lb", "blb",
    ],
    "稀神探女": [
        75,
        "xishen", "tannv", "xstn", "xs", "tn",
        "kishin", "sagume",
        "hxd", "zsz", "jz", "gzy", "ttn",
    ],
    "赫卡提亚": [
        76,
        "hekatiya", "labisilazuli", "hkty", "lbslzl", "hk", "heka",
        "hecatia", "lapislazuli",
        "nvshen", "ns", "wqns", "tx", "ts",
    ],
    "拉尔瓦": [
        77,
        "aitaniti", "laerwa", "lew",
        "eternity", "larva",
        "eight", "ba", "dez", "cys", "ms", "plez", "ez",
    ],
    "坂田合欢": [
        78,
        "bantian", "hehuan", "bthh", "bt", "hh", "hehuannai", "hhn",
        "sakata", "nemuno",
        "huanjie", "hj", "daojie", "cdj",
    ],
    "高丽野阿吽": [
        79,
        "gaoliye", "ahong", "glyah", "gly", "ah",
        "komano", "aunn",
        "ss", "bq", "boquan", "ssz", "szg",
    ],
    "矢田寺成美": [
        80,
        "shitiansi", "chengmei", "stscm", "sts", "cm",
        "yatadera", "narumi",
        "dz", "dizang", "yuegong", "yg", "rcm",
    ],
    "摩多罗隐岐奈": [
        81,
        "moduoluo", "yinqinai", "mdl", "yqn", "mdlyqn",
        "matara", "okina",
        "ly", "lunyi", "ms", "mishen", "lzs", "otto", "dg",
    ],
    "梅蒂欣·梅兰可莉": [
        82,
        "meidixin", "meilankeli", "mdx", "mlkl",
        "medicine", "melancholy",
        "dro", "md", "llh", "linglan", "xiaodu", "xd", "meidi", "md",
    ],
    "稗田阿求": [
        83,
        "baitian", "aqiu", "btaq", "bt", "aq",
        "hieda", "akyuu",
        "aqn", "klsq", "ajs", "laoda", "ld",
        "lingqiu", "lq",
    ],
    "大妖精": [
        84,
        "dayaojing", "dyj",
        "daiyousei", "dys",
        "dajiang", "dj", "yjz", "yj", "daichan", "dc",
    ],
    "若鹭姬": [
        85,
        "ruoluji", "rlj",
        "wakasagihime",
        "ry",
        "cgyg",
    ],
    "清兰": [
        86,
        "qinglan", "ql",
        "seiran",
        "lt", "ltz",
    ],
    "哆来咪·苏伊特": [
        87,
        "duolaimi", "suyite", "dlmsyt", "dlm", "syt",
        "doremy", "sweet",
        "yes", "mo", "gzz",
    ],
    "克劳恩皮丝": [
        88,
        "kelaoen", "pisi", "kleps", "kle", "ps",
        "clown", "piece", "cp",
        "xyj", "mg", "meiguo", "mgxyj", "klp", "gcyj", "xiaochou", "xc",
    ],
    "丁礼田舞": [
        89,
        "dinglitian", "wu", "dltw", "dlt", "w",
        "teireida", "mai",
        "gw", "gwjm",
    ],
    "尔子田里乃": [
        90,
        "erzitian", "linai", "eztln", "ezt", "ln",
        "nishida", "satono",
        "gw", "gwjm",
    ],
    "绵月丰姬": [
        91,
        "mianyue", "fengji", "myfj", "my", "fj",
        "watatsuki", "toyohime",
        "myjm", "yr",
    ],
    "绵月依姬": [
        92,
        "mianyue", "yiji", "myyj", "my", "yj",
        "watatsuki", "yorihime",
        "myjm", "yr",
    ],
    "秦心": [
        93,
        "qin", "xin", "qx", "q", "x",
        "hata", "kokoro",
        "xx", "xj", "mlq",
    ],
    "九十九弁弁": [
        94,
        "jiushijiu", "bianbian", "jsjbb", "jsj", "bb",
        "tsukumo", "benben",
    ],
    "九十九八桥": [
        95,
        "jiushijiu", "baqiao", "jsjbq", "jsj", "bq",
        "tsukumo", "yatsuhashi",
        "jjb",
    ],
    "琪斯美": [
        96,
        "qisimei", "qsm",
        "kisume",
        "xiaotong", "xt", "dp",
    ],
    "铃瑚": [
        97,
        "linghu", "lh",
        "ringo",
        "htz", "tz",
    ],
    "纯狐": [
        98,
        "chunhu", "ch", "chh",
        "junko",
        "lfy", "chunma", "cm",
    ],
    "小恶魔": [
        99,
        "xiao", "emo", "xiaoemo", "xem", "em",
        "little", "devil", "koakuma", "akuma",
        "tsgly",
    ],
    "今泉影狼": [
        100,
        "jinquan", "yinglang", "jqyl", "jq", "yl",
        "imaizumi", "kagerou",
        "cgyg", "ml", "lj",
    ],
    "鬼人正邪": [
        101,
        "guiren", "zhengxie", "grzx", "gr", "zx",
        "kijin", "seija",
        "fgz", "xzrg",
    ],
    "吉吊八千慧": [
        102,
        "jidiao", "baqianhui", "jdbqh", "jd", "bqh",
        "kitcho", "yachie",
    ],
    "骊驹早鬼": [
        103,
        "liju", "zaogui", "ljzg", "lj", "zg",
        "kurokoma", "saki",
        "tianma", "tm", "htm",
    ],
    "本居小铃": [
        104,
        "benju", "xiaoling", "bjxl", "bj", "xl",
        "motoori", "kosuzu",
        "fzt", "sm", "shuima", "zuosi", "zsl", "zs",
        "lingqiu", "lq",
    ],
    "依神女苑": [
        105,
        "yishen", "nvyuan", "ysny", "ys", "ny",
        "yorigami", "jyoon",
        "pqjm", "syw", "zcjj",
    ],
    "依神紫苑": [
        106,
        "yishen", "ziyuan", "yszy", "ys", "zy",
        "yorigami", "shion",
        "pqjm", "tyml", "wcjj",
    ],
    "庭渡久侘歌": [
        107,
        "tingdu", "jiuchage", "tdjcg", "td", "jcg",
        "niwatari", "kutaka",
        "jimei", "jm", "cxk", "js", "j",
    ],
    "饕餮尤魔": [
        108,
        "taotie", "youmo", "ttym", "tt", "ym",
        "toutetsu", "yuma",
        "zuzhang", "zz", "tmz", "xzym",
    ],
    "铃仙二号": [
        109,
        "lingxian", "erhao", "lx", "eh", "lxeh"
        "reisen",
        "linger", "le", "ertu", "et",
    ],
    "魅魔": [
        110,
        "meimo", "mm",
        "mima",
        "el", "jzstw", "stw",
    ],
    "戎璎花": [
        111,
        "rong", "yinghua", "ryh", "yh",
        "ebisu", "eika",
        "shuizi", "sz",
    ],
    "牛崎润美": [
        112,
        "niuqi", "runmei", "nqrm", "nq", "rm",
        "ushizaki", "urumi",
        "niuma", "nm", "niujie", "nj", "ng",
    ],
    "山城高岭": [
        113,
        "shancheng", "gaoling", "scgl", "sc", "gl",
        "yamashiro", "takane",
        "shantong", "st", "scsq",
    ],
    "菅牧典": [
        114,
        "jianmu", "dian", "jmd", "jm", "d",
        "kudamaki", "tsukasa",
        "adian", "ad", "guanhu", "gh", "xhl", "hl", "fh",
    ],
    "饭纲丸龙": [
        115,
        "fangang", "wanlong", "fgwl", "fg", "wl",
        "iizunamaru", "megumu",
        "dtg", "along", "al", "longlong", "ll", "fanwan", "fw",
    ],
    "天弓千亦": [
        116,
        "tiangong", "qianyi", "tgqy", "tg", "qy",
        "tenkyu", "chimata",
        "jialing", "jl", "scs",
    ],
    "奥野田美宵": [
        117,
        "aoyetian", "meixiao", "aytmx", "ayt", "mx",
        "okunoda", "miyoi",
        "jym", "jy",
    ],
    "杖刀偶磨弓": [
        118,
        "zhangdaoou", "mogong", "zdomg", "zdo", "mg",
        "joutougu", "mayumi",
        "zhilun", "zl", "ym", "bmy", "omg",
    ],
    "埴安神袿姬": [
        119,
        "zhianshen", "guiji", "zasgj", "zas", "gj",
        "haniyasushin", "keiki",
        "guangxi", "gx", "gxdm", "dama", "dm", "zz", "dangao", "dg",
    ],
    "豪德寺三花": [
        120,
        "haodesi", "sanhua", "hdssh", "hds", "sh",
        "goutokuji", "mike",
        "djmm", "maike", "mk", "djj", "shd",
    ],
    "驹草山如": [
        121,
        "jucao", "shanru", "jcsr", "jc", "sr",
        "komakusa", "sannyo",
        "jctf", "tf",
    ],
    "玉造魅须丸": [
        122,
        "yuzao", "meixuwan", "yzmxw", "yz", "mxw",
        "tamatsukuri", "misumaru",
        "dama", "dm", "yuma", "ym", "zaojie", "zj", "gys", "sgs",
    ],
    "姬虫百百世": [
        123,
        "jichong", "baibaishi", "jcbbs", "jc", "bbs",
        "himemushi", "momoyo",
        "dwg", "wg", "wcjj", "gryy",
    ],
    "孙美天": [
        124,
        "sun", "meitian", "smt", "s", "mt",
        "son", "biten",
        "yuanshen", "ys", "dasheng", "ds", "swk", "qtds", "houge", "hg", "hj",
    ],
    "三头慧之子": [
        125,
        "santou", "huizhizi", "sthzz", "st", "hzz",
        "mitsugashira", "enoko",
        "jzg", "lsg", "hgz", "sllhdg",
    ],
    "天火人血枪": [
        126,
        "tianhuoren", "xueqiang", "thrxq", "thr", "xq",
        "tenkajin", "chiyari",
        "ts", "tx", "otaku", "xqj",
    ],
    "豫母都日狭美": [
        127,
        "yumudu", "rixiamei", "ymdrxm", "ymd", "rxm",
        "yomotsu", "hisami",
        "hqcn", "qiezi", "qz", "qzj", "spt", "gzk",
    ],
    "日白残无": [
        128,
        "ribai", "canwu", "rbcw", "rb", "cw",
        "nippaku", "zanmu",
        "brcw",
    ],
    "朱鹭子": [
        129,
        "zhuluzi", "zlz",
        "unnamed", "book", "reading", "youkai", "tokiko",
        "dsyg", "wuming", "dushu", "zl",
    ],
    "冈崎梦美": [
        130,
        "gangqi", "mengmei", "gqmm", "gq", "mm",
        "yumemi", "okazaki",
        "jiaoshou", "js", "caomei", "cm", "jzstw",
    ],
    "北白河千百合": [
        131,
        "beibaihe", "qianbaihe", "bbhqbh", "bbh", "qbh",
        "chiyuri", "kitashirakawa",
        "zdkm", "zdjsz",
    ],
    "卡娜·安娜贝拉尔": [
        132,
        "kana", "annabeilaer", "knanble", "kn", "anble",
        "anaberal",
        "mxs", "lpn", "bjsn", "anklnn",
    ],
    "奥莲姬": [
        133,
        "aolianji", "alj",
        "orange",
        "chengzi", "cz", "juzi", "jz",
    ],
    "小兔姬": [
        134,
        "xiaotuji", "xtj", "xt",
        "kotohime",
        "jingcha", "jc",
    ],
    "梦月": [
        135,
        "mengyue",
        "mugetsu",
    ],
    "幻月": [
        136,
        "huanyue",
        "gengetsu",
    ],
    "幽香（旧作）": [
        137,
        "youxiang", "yx",
        "yuka",
        "smr", "jzstw",
    ],
    "明罗": [
        138,
        "mingluo",
        "meira",
    ],
    "朝仓理香子": [
        139,
        "zhaocang", "lixiangzi", "zclxz", "zc", "lxz", "cc", "cclxz",
        "rikako", "asakura",
    ],
    "爱莲": [
        140,
        "ailian", "al",
        "ellen",
        "lamn", "ailun", "pst", "ps",
    ],
    "胡桃": [
        141,
        "hutao", "ht",
        "kurumi",
        "xxg", "vampire",
    ],
    "艾丽": [
        142,
        "aili", "al",
        "elly",
        "menwei", "mw",
    ],
    "里香": [
        143,
        "lixiang", "lx",
        "rika",
        "zhanche", "zc", "zcsn",
    ],
    "依莉斯": [
        144,
        "yilisi", "yls",
        "elis",
    ],
    "冴月麟": [
        145,
        "huyuelin", "hyl", "yyl",
        "satsuki", "rin",
        "akl",
    ],
    "宫出口瑞灵": [
        146,
        "gongchukou", "ruiling", "gckrl", "gck", "rl",
        "miyadeguchi", "mizuchi",
        "fanyuwang", "fyw",
    ],
    "幽幻魔眼": [
        147,
        "youhuanmoyan", "yhmy", "yh", "youxuanmoyan", "yxmy", "yx",
        "yuugenmagan",
    ],
    "梦子": [
        148,
        "mengzi", "mz",
        "yumeko",
        "mjnp",
    ],
    "爱丽丝（旧作）": [
        149,
        "ailisi", "als",
        "alice",
        "lls", "xxa",
    ],
    "留琴": [
        150,
        "liuqin", "lq",
        "rukoto", "rkt",
        "hnnp", "h",
    ],
    "矜羯罗": [
        151,
        "jinjieluo", "jjl",
        "konngara",
    ],
    "神玉": [
        152,
        "shenyu", "sy"
        "singyoku",
    ],
    "神绮": [
        153,
        "shenqi", "sq",
        "shinki",
        "taitai", "tt", "dms", "neg", "jzstw",
    ],
    "舞": [
        154,
        "wu", "w",
        "mai",
        "bzmfs",
    ],
    "菊理": [
        155,
        "juli", "jl",
        "kikuri",
    ],
    "萨丽爱尔": [
        156,
        "saliaier", "slae",
        "sariel",
        "dsg",
    ],
    "萨拉": [
        157,
        "sala",
        "sara",
    ],
    "蕾拉·普莉兹姆利巴": [
        158,
        "leila", "pulizimuliba", "ll", "plzmlb",
        "leira", "prismriver",
        "ljh", "sl",
    ],
    "雪": [
        159,
        "xue", "x",
        "yuki",
        "hzmfs",
    ],
    "露易兹": [
        160,
        "luyizi", "lyz",
        "luize",
    ],
    "其他": [
        161,
        "qt", "qita",
    ],
    "旧作": [
        162,
        "jiuzuo", "heilishi", "jz", "hls", "qt",
    ],
    "同人二创": [
        163,
        "tongren", "erchuang", "trec", "tr", "ec", "qt",
    ],
    "cosplay": [
        164,
        "cosplay", "cos", "qt", "cp",
    ]
}
