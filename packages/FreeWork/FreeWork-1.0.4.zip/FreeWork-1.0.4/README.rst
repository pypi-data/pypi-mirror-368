**★ 关于FreeWork的相关介绍 (Introduction for FreeWork)★**

*本文档为中英双语文档，其中括号内的为中文部分的英语译文，其二者内容相同。(This document is a bilingual document in Chinese and English, with the English translation of the Chinese part enclosed in parentheses, both of which have the same content.)*

**函数目录 (List of Function)**

**· 文件复制函数/File Copy Function：**
copyFile(FileOriginalPath, FileNewPath)

**· 文件剪切函数/File Move Function：**
moveFile(FileOriginalPath, FileNewPath)

**· Excle读取函数/Excel Read Function：**
excleRead(ExclePath, SheetIndex, Rowlow, Rowmax, Collow, Colmax)

**· Excle写入函数/Excel Write Function：**
excleWrite(ExclePath, SheetIndex, CellRow, CellCol, Value, SaveAsNewFile(True / False))

**· Word表格读取函数/Word Table Reading Function：**
wordTableRead(WordPath, TableIndex)

**· Word表格写入函数/Word Table Writing Function：**
wordTableWrite(WordPath, TableIndex, Row, Col, InputText, SaveAsNewFile(True / False))

**· Word表格追加图片函数（不删除原有文字）/Word Table Append Image Function (Doesn't delete original text)：**
wordTableInsertFig(WordPath, TableIndex, Row, Col, ImagePath, ImageHeight_cm, ImageWidth_cm, SaveAsNewFile)

**· Word表格单元格对齐设置函数/Word Table Cell Alignment Setting Function：**
wordTableParaAlignment(WordPath, TableIndex, Row, Col, Alignment_left_right_center_None, SaveAsNewFile)

**· Word写入函数/Word Write Function：**
wordParagraphAdd(wordPath, wordSavePath, new_text, FontName, FontSize, IsBold, IsItalic):

**· Word新段写入函数/Word Write Paragraph Function：**
wordAdd(wordPath, wordSavePath, new_text, FontName, FontSize, IsBold, IsItalic, Indent)

**· Shapefile转出Excle函数/Shapefile Exporting Excel Function：**
shpToXlsx(ShpPath, XlsxPath)

**· Word段落格式获取函数/Word Paragraph Format Get Function：**
wordParaFormat(wordPath)

**· Word段落插入函数/Word Paragraph Insertion Function：**
wordInsertText(WordPath, Text, ParaIndex, NewParagraph=True, StyleName=None)

**· Word公式插入函数/Insert Function in Word Formula：**
wordInsertLatexFormula(WordPath, ParaIndex, LatexCode, NewParagraph=True)

**一、安装 (Installation)**

.. code:: python

    pip install FreeWork

**二、使用 (Usage)**

**1. 导包 (Import)**

.. code:: python

    from FreeWork import office as ow

**2. 内置函数 (Integrated functions)**

**(1) 文件复制函数 (File Copy Function)**

本函数用于复制文件，在复制的同时可以根据需求修改函数名字。通常与for循环结合进行批量复制并改名的操作。(This function is used to copy files, and the function name can be modified as needed while copying. Usually combined with the for loop for batch copying and renaming operations.)

.. code:: python

    from FreeWork import office as ow

    ow.copyFile(FileOriginalPath, FileNewPath)
    # ow.copyFile(文件原始路径, 文件新路径)

*注意，这里文件路径为包含文件名的路径，可以是相对路径，也可以是绝对路径。如：(1)D:\Example\EasyWork\example.png;(2)\Example\example.png。*

*(Note that the file path here is a path that includes the file name, which can be a relative path or an absolute path. For example:(1)D:\Example\EasyWork\example.png;(2)\Example\example.png)*

**(2) 文件剪切函数 (File Move Function)**

本函数用于剪切文件，在剪切的同时可以根据需求修改函数名字。通常与for循环结合进行批量剪切并改名的操作。(This function is used to move files, and the function name can be modified as needed while moving. Usually combined with the for loop for batch move and renaming operations.)

.. code:: python

    from FreeWork import office as ow

    ow.moveFile(FileOriginalPath, FileNewPath)
    # ow.moveFile(文件原始路径, 文件新路径)

*注意，这里文件路径为包含文件名的路径，可以是相对路径，也可以是绝对路径。如：(1)D:\Example\EasyWork\example.jpg;(2)\Example\example.jpg。*

*(Note that the file path here is a path that includes the file name, which can be a relative path or an absolute path. For example:(1)D:\Example\EasyWork\example.jpg;(2)\Example\example.jpg)*

**(3) Excle读取函数 (Excel Read Function)**

.. code:: python

    from FreeWork import office as ow

    List = ow.excleRead(ExclePath, SheetIndex, Rowlow, Rowmax, Collow, Colmax)
    # ow.excleRead(Excle路径, Sheet序号, 最小行号, 最大行号, 最小列号, 最大列号)

*注意，这里所有的序号均是从1开始而不是0！而且列号为数字，请不要填写字母。文件路径同样为包含文件名的路径，可以是相对路径，也可以是绝对路径，与前面的函数所需的路径形式相同。(Note that all serial numbers here start from 1 instead of 0! And the column number is a number, please do not fill in letters.The file path is also a path that includes the file name, which can be a relative path or an absolute path, in the same form as the path required by the previous function.)*

比如我需要获取example.xlsx中sheet1的(2,3)到(5,7)的所有数据，则应当如下调用：

(For example, if I need to retrieve all the data from (2,3) to (5,7) of Sheet1 in example.xlsx, I should call as follows:)

.. code:: python

    from FreeWork import office as ow

    List = ow.excleRead("\Example\example.xlsx", 1, 2, 5, 3, 7)

**(4) Excle写入函数 (Excel Write Function)**

.. code:: python

    from FreeWork import office as ow

    ow.excleWrite(ExclePath, SheetIndex, CellRow, CellCol, Value, SaveAsNewFile(True / False))
    # ow.excleWrite(Excle路径, Sheet序号, 单元格行号, 单元格列号, 要赋的值, 是否保存为新文件(True/False))

*注意，这里所有的序号均是从1开始而不是0！而且列号为数字，请不要填写字母。文件路径同样为包含文件名的路径，可以是相对路径，也可以是绝对路径，与前面的函数所需的路径形式相同。(Note that all serial numbers here start from 1 instead of 0! And the column number is a number, please do not fill in letters.The file path is also a path that includes the file name, which can be a relative path or an absolute path, in the same form as the path required by the previous function.)*

本函数只能填写单个单元格，若需批量填写，可与for循环等结合使用。(This function can only fill in a single cell. If batch filling is required, it can be used in conjunction with for loops, etc.)

**(5) Word表格读取函数 (Word Table Reading Function)**

.. code:: python

    from FreeWork import office as ow

    List = ow.wordTableRead(WordPath, TableIndex)
    # ow.wordTableRead(Word路径, 表格索引)

*注意，这里表格索引为全局索引。文件路径同样为包含文件名的路径，可以是相对路径，也可以是绝对路径，与前面的函数所需的路径形式相同。(Note that the table index here is a global index. The file path is also a path that includes the file name, which can be a relative path or an absolute path, in the same form as the path required by the previous function.)*

**(6) Word表格写入函数 (Word Table Writing Function)**

.. code:: python

    from FreeWork import office as ow

    ow.wordTableWrite(WordPath, TableIndex, Row, Col, InputText, SaveAsNewFile(True / False))
    # ow.wordTableWrite(Word路径, 表格索引, 行号, 列号, 欲写入的文本, 是否保存为新文件(True/False))

*注意，这里行号与Excle的不同，加入表格1的未合并前为6个单元格，此时将1、2单元格合并。此时“行号”参数填写1与2均会写入第一个单元格，当填入3时才会写入第二个单元格。列与行的情况相同。(Note that the row numbers here are different from Excel. Before joining Table 1, there are 6 unmerged cells. In this case, cells 1 and 2 will be merged. At this point, filling in 1 and 2 for the "line number" parameter will be written to the first cell, and only when filling in 3 will it be written to the second cell. The situation is the same for columns and rows.)*

**· 如果想要插入如下的上标下标 (If you want to insert the following superscript and subscript)**

.. math::

    面积 S_1=123 hm^2

它的代码应该如下所示 (Its code should look like this)：

.. code:: python

    from FreeWork import office as ow

    ow.wordTableWrite(WordPath, TableIndex, Row, Col, "面积 S_(1)=123 hm^(2)", SaveAsNewFile(True / False))
    # ow.wordTableWrite(Word路径, 表格索引, 行号, 列号, 欲写入的文本, 是否保存为新文件(True/False))

*其中括号是必不可少的，否则“^”符号后面的所有文本均将以上标的形式写入段落，“_”符号后面的所有文本均将以下标的形式写入段落，直至本条插入文本结束！还有请注意，这里括号需以英文状态下输入，否则将不会起到其应有的作用。(Parentheses are essential, if there are no parentheses, all text after the "^" symbol will be written to the paragraph in the above form, and all text after the "_" symbol will be written to the paragraph in the following form until the end of the inserted text in this article! Also, please note that the parentheses need to be entered in English, otherwise they will not play their proper role.)*

**(7) Word表格追加图片函数/不删除原有文字 (Word Table Append Image Function / Doesn't delete original text)**

.. code:: python

    from FreeWork import office as ow

    ow.wordTableInsertFig(WordPath, TableIndex, Row, Col, ImagePath, ImageHeight_cm, ImageWidth_cm, SaveAsNewFile)
    # ow.wordTableInsertFig(Word路径, 表格索引, 行号, 列号, 图片路径, 插入后图片的高度（厘米为单位）, 插入后图片的宽度（厘米为单位）, 是否保存为新文件(True/False))

*注意，这里图片高度可以为“None”，行号列号规则与函数(6)相同。(Note that the height of the image here can be "None", and the row and column numbering rules are the same as function (6).)*

**(8) Word表格单元格对齐设置函数 (Word Table Cell Alignment Setting Function)**

.. code:: python

    from FreeWork import office as ow

    ow.wordTableParaAlignment(WordPath, TableIndex, Row, Col, Alignment_left_right_center_None, SaveAsNewFile)
    # ow.wordTableParaAlignment(Word路径, 表格索引, 行号, 列号, 对齐方式, 是否保存为新文件(True/False))

*注意，对齐方式只能填写left/right/center/None，否则均会设置为None两端对齐。(Note that the alignment method can only be left/right/center/None, otherwise it will be set to None for both ends alignment.)*

**(9) Shapefile转出Excle函数 (Shapefile Exporting Excel Function)**

.. code:: python

    from FreeWork import office as ow

    ow.shpToXlsx(ShpPath, XlsxPath)
    # ow.shpToXlsx(Shp路径, Xlsx路径)

*注意，文件路径同样为包含文件名的路径，可以是相对路径，也可以是绝对路径，与前面的函数所需的路径形式相同。(Note that the file path is also a path that includes the file name, which can be a relative path or an absolute path, in the same form as the path required by the previous function.)*

**三、反馈与改进 (Feedback and improvement)**

本程序包将继续完善，在第二个版本上架时将会发布CSND的解析与教程，后续还会发布Bilibili的视频教程。若在此期间遇到任何问题，欢迎与作者联系。
(This package will continue to be improved, and CSND parsing and tutorials will be released when the second version is launched. Bilibili video tutorials will also be released in the future. If you encounter any problems during this period, please feel free to contact the author.)

中国大陆的朋友可以通过QQ或邮箱的形式与作者取得联系，
中国台湾、中国香港、中国澳门以及海外的朋友欢迎通过邮件的形式与作者交流，
作者收到反馈消息后将第一时间进行反馈！
(Friends in Chinese Mainland can contact the author via QQ or email. Friends in China Taiwan, China Hong Kong, China Macao and overseas are welcome to communicate with the author via email. The author will give feedback as soon as he receives the feedback!)

**称呼：**
王先生 (
**Name:**
Jhonie)

**E-mail：**
queenelsaofarendelle2022@gmail.com / 2570518164@qq.com

**QQ：**
2570518164
