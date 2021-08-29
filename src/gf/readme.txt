截图工具使用说明：
chapter_page_info.json 文件说明：
"9": [15, 4] 表示第9章内容从pdf第15页开始，而且该页中包含了4个属于第9章的字，以此类推，需要把对应的章节的信息补充完整

执行下面的命令进行截图，参数可根据下面的说明，动态选择
cut_picture.exe --pdf_file "D:\work\gf\截图\世尊寺本字镜.pdf" --picture_path "D:\work\gf\截图\pictures"  --chapter_num 16 --top_side 170 --right_side 80 --x_step 73 --y_step 139
参数说明：
    parser.add_argument('--pdf_file', help='PDF文件路径', type=str, required=True)
    parser.add_argument('--picture_path', help='截图存放路径', type=str, required=True)
    parser.add_argument('--chapter_num', help='第几章', type=int, default=16, required=False)
    parser.add_argument('--page_num', help='第几页, 如果不指定页码，默认为9999，代表截图整章(除了该章第一页)', type=int, default=None, required=False)
    parser.add_argument('--top_side', help='上边界距离截图区宽度', type=float, default=170, required=False)
    parser.add_argument('--right_side', help='右边界距离截图区宽度', type=float, default=80, required=False)
    parser.add_argument('--x_step', help='水平方向每次换列截图时增加的步长', type=float, default=73, required=False)
    parser.add_argument('--y_step', help='竖直方向每次换行截图时增加的步长', type=float, default=139, required=False)



插图工具使用说明：
执行下面的命令进行插图
insert_picture.exe --word_file "D:\work\gf\截图\16.第十六 忄篇540.docx"  --picture_path "D:\work\gf\截图\pictures\16"  --picture_height 2400000
参数说明：
--word_file 指需要插入的word路径
--picture_path 指需要插入的图片文件夹，该文件夹中存放着需要插入的图片
--picture_height 指word中插入的图片高度，可以根据需要自行调整