★ 关于FreeWork的相关介绍 (Introduction for FreeWork)★

*本文档为中英双语文档，其中括号内的为中文部分的英语译文，其二者内容相同。(This document is a bilingual document in Chinese and English, with the English translation of the Chinese part enclosed in parentheses, both of which have the same content.)*

函数目录 (List of Functions)
=============================

· 文件名和父路径获取函数 / File Name and Parent Folder Functions
------------------------------------------------------------------

- **fileName(FilePath)**
  获取给定路径所指向文件的文件名。
  (Get the file name from a given file path.)

- **fileFatherPath(FilePath)**
  获取给定路径所指向文件的父文件夹路径。
  (Get the parent folder path from a given file path.)

· 文件复制与剪切函数 / File Copy and Move Functions
---------------------------------------------------

- **copyFile(FileOriginalPath, FileNewPath)**
  复制文件，支持相对或绝对路径，自动创建目标文件夹。
  (Copy files with support of relative or absolute paths; create target folder automatically.)

- **moveFile(FileOriginalPath, FileNewPath)**
  剪切（移动）文件，支持相对或绝对路径，自动创建目标文件夹。
  (Move files with support for relative or absolute paths; auto-create target folder.)

· Excel读写函数 / Excel Read and Write Functions
--------------------------------------------------

- **excleRead(ExclePath, SheetIndex, Rowlow, Rowmax, Collow, Colmax)**
  读取指定Excel工作簿、指定工作表中指定行列范围数据（起始均从1）。返回二维列表或者一维列表，单元格数据保持原型。
  (Read specified Excel sheet and range data starting from 1-based indices; returns list of lists or list.)

- **excleWrite(ExclePath, SheetIndex, Row, Col, Value, SaveAsNewFile)**
  向指定Excel单元格写入数据，可选择覆盖原文件或另存为新文件。行列均从1开始。
  (Write data at specified Excel cell, support save as new file or overwrite.)

· Word表格操作函数 / Word Table Functions
-------------------------------------------

- **wordTableRead(WordPath, TableIndex)**
  读取Word文档中指定索引表格的所有单元格数据（表格索引从1开始）。返回二维列表。
  (Read all cell data from a Word table by index, returns list of lists.)

- **wordTableWrite(WordPath, TableIndex, Row, Col, Text, SaveAsNewFile)**
  向Word表格指定单元格写入文本，支持插入格式化的上下标（需英文括号标记），支持是否保存为新文件。
  (Write text to Word table cell; supports superscript/subscript markers ^() _(); save as new file or not.)

- **wordTableInsertFig(WordPath, TableIndex, Row, Col, ImagePath, ImageHeight_cm, ImageWidth_cm, SaveAsNewFile)**
  向Word指定表格单元格追加图片（不删除原文字），支持指定图片高度和宽度（厘米为单位），可保存新文件或覆盖。
  (Append image to Word table cell without deleting text; size optional; save options.)

- **wordTableParaAlignment(WordPath, TableIndex, Row, Col, Alignment_left_right_center_None, SaveAsNewFile)**
  设置Word表格单元格内段落的对齐方式，只支持 left/right/center/None。可另存新文件或覆盖。
  (Set paragraph alignment inside Word table cell; options left, right, center, none.)

- **wordTableWriteExtend(WordPath, TableIndex, Row, Col, Text, StyleName=None, Alignment=None)**
  兼容扩展写入，自动按需新增行复制上一行格式，支持段落样式与对齐设置。
  (Extended write: auto-add rows with copied format; support paragraph styles and alignment.)

- **wordDeleteTable(WordPath, TableIndex)**
  删除指定索引的表格，并覆盖保存Word文件。
  (Delete specified table by index and overwrite Word file.)

- **wordDeleteTableRow(WordPath, TableIndex, RowIndex)**
  删除Word文档中指定表格的指定行，并覆盖保存文档。
  (Delete specified row from table in Word file and overwrite.)

· Word段落操作函数 / Word Paragraph Functions
-----------------------------------------------

- **wordAdd(wordPath, wordSavePath, new_text, FontName=None, FontSize=None, IsBold=None, IsItalic=None)**
  在文档末尾追加文本（同段落），支持设置字体、字号、加粗、斜体。
  (Append text at document end inline; support font name, size, bold, italic.)

- **wordParagraphAdd(wordPath, wordSavePath, new_text, FontName=None, FontSize=None, IsBold=None, IsItalic=None, Indent=None, Alignment="l")**
  在文档末尾新建段落插入文本，支持字体、字号、加粗、斜体、首行缩进及段落对齐。
  (Add new paragraph at document end with text; supports font, size, bold, italic, indent, alignment.)

- **wordParaFormat(wordPath)**
  获取文档最后一段的段落格式对象。
  (Get paragraph format object of the last paragraph in document.)

- **insert_paragraph_after(paragraph, text=None, style=None)**
  在指定段落后插入新段落，支持传入文本和样式名，返回新段落对象。
  (Insert new paragraph after specified paragraph, optional text and style.)

- **wordInsertText(WordPath, Text, ParaIndex, NewParagraph=True, StyleName=None)**
  在指定.docx文件指定段落（索引从0起）后插入文本，新建段落或追加文本可选，支持样式，文档空时自动创建第一段。
  (Insert text after specified paragraph index in Word; new paragraph or append; supports style; auto-create if empty.)

- **wordReplaceParagraphText(WordPath, Text, ParaIndex, StyleName=None)**
  替换Word文档指定段落所有文本，支持样式，越界自动调整，文档无段自动新建。
  (Replace all text of specified paragraph with style; index bounds checked; auto-create if empty.)

- **wordFindParagraphIndexesByMark(WordPath, MarkString)**
  返回包含指定字符串的所有段落索引列表（0开始）。
  (List paragraph indexes containing specified substring.)

- **wordFindParagraphTextsByMark(WordPath, MarkString)**
  返回所有包含指定子串的段落完整文本列表。
  (List paragraph texts containing substring.)

- **wordDeleteParagraph(WordPath, ParaIndex)**
  删除指定索引的段落，并覆盖保存Word文件。
  (Delete specified paragraph by index and overwrite Word file.)

· Word查找表格索引函数 / Word Table Index Finders
----------------------------------------------------

- **wordFindTableIndexByMark(WordPath, MarkRow, MarkString)**
  查找Word文档中所有在指定行（1起）包含指定标记字符串的表格索引列表。
  (Find all table indexes where specified row contains given string.)

- **wordFindCellsByMark(WordPath, MarkString)**
  查找Word文档中所有包含指定标记字符串的单元格，返回格式为 [表格索引, 行号, 列号]（均从1开始）的列表。
  (Find all cells containing specified string, return list of [tableIndex, rowIndex, colIndex].)

· Shapefile转Excel函数 / Shapefile to Excel
---------------------------------------------

- **ShpToXlsx(ShpPath, XlsxPath)**
  利用fiona和pandas将Esri Shapefile中的属性表导出为Excel文件。
  (Export attribute table from Esri Shapefile to Excel file via fiona and pandas.)

· Word插入LaTeX公式函数 / Word Insert LaTeX Formula
-----------------------------------------------------

- **wordInsertLatexFormula(WordPath, ParaIndex, LatexCode, NewParagraph=True)**
  利用Spire.Doc在指定段落插入LaTeX数学公式，新建段落或追加可选。自动创建空段。
  (Insert LaTeX math formula at specified paragraph of Word using Spire.Doc library.)

· 新增函数 / New Functions
---------------------------

- **TextType (Enum)**

  定义文本类型的枚举，区分普通文本和公式。
  (Enumeration to distinguish text and formula types.)

- **parse_text_and_formula(text)**

  解析输入字符串，自动识别并拆分成普通文本和多种LaTeX数学公式（支持`$$...$$`、`$...$`、`\(...\)`和`\[...\]`标记），返回列表格式为 `[类型, 内容]`。

  (Parse input text to separate plain text and LaTeX formula parts, supporting common delimiters; returns list of [type, content].)

  :param text: 原始字符串 (Original string)
  :return: list，元素格式为 [[TextType.Text or TextType.Formula, 内容], ...] (List of parsed segments with type and content)

---

安装 (Installation)
===================

.. code:: bash

    pip install FreeWork

使用示例 (Usage Examples)
==========================

.. code:: python

    from FreeWork import office as ow
    from FreeWork import TextType
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    # 复制文件
    ow.copyFile("source.png", "dest/new_source.png")

    # 移动文件
    ow.moveFile("source.txt", "dest/new_source.txt")

    # 读取Excel数据
    data = ow.excleRead("example.xlsx", SheetIndex=1, Rowlow=2, Rowmax=5, Collow=3, Colmax=7)

    # Excel写数据
    ow.excleWrite("example.xlsx", SheetIndex=1, Row=3, Col=4, Value="测试值", SaveAsNewFile=True)

    # 读取Word表格
    table_data = ow.wordTableRead("doc.docx", TableIndex=1)

    # 写Word表格带上下标文本
    ow.wordTableWrite("doc.docx", TableIndex=1, Row=2, Col=3, Text="面积 S_(1)=123 hm^(2)", SaveAsNewFile=False)

    # 向Word表格添加图片
    ow.wordTableInsertFig("doc.docx", TableIndex=1, Row=1, Col=2, ImagePath="img.png", ImageHeight_cm=5, ImageWidth_cm=None, SaveAsNewFile=True)

    # Word表格单元格对齐
    ow.wordTableParaAlignment("doc.docx", TableIndex=1, Row=1, Col=2, Alignment_left_right_center_None="center", SaveAsNewFile=False)

    # 新段落插入文字
    ow.wordInsertText("doc.docx", "新内容", ParaIndex=2, NewParagraph=True, StyleName="Normal")

    # 替换段落文本
    ow.wordReplaceParagraphText("doc.docx", Text="替换内容", ParaIndex=5, StyleName="Normal")

    # 查找包含标记的表格索引
    indexes = ow.wordFindTableIndexByMark("doc.docx", MarkRow=1, MarkString="关键字")

    # 查找包含标记的段落索引
    para_indexes = ow.wordFindParagraphIndexesByMark("doc.docx", "关键字")

    # 查找包含标记的段落文本
    texts = ow.wordFindParagraphTextsByMark("doc.docx", "关键字")

    # 查找包含标记的单元格坐标列表
    cell_positions = ow.wordFindCellsByMark("doc.docx", "关键字")

    # Shapefile转Excel
    ow.ShpToXlsx("example.shp", "output.xlsx")

    # Word文档末尾追加文字（同段）
    ow.wordAdd("doc.docx", "doc_modified.docx", "追加文字", FontName="宋体", FontSize=Pt(12), IsBold=True, IsItalic=False)

    # Word文档末尾添加新段落
    ow.wordParagraphAdd("doc.docx", "doc_modified.docx", "新段落文字", FontName="Calibri", FontSize=Pt(11), IsBold=False, IsItalic=False, Indent=None, Alignment="j")

    # 向指定单元格扩展写入，自动新增行
    ow.wordTableWriteExtend(
        WordPath="doc.docx",
        TableIndex=1,
        Row=10,
        Col=1,
        Text="延伸写入",
        StyleName="Normal",
        Alignment=WD_ALIGN_PARAGRAPH.CENTER
    )

    # 删除指定段落
    ow.wordDeleteParagraph("doc.docx", ParaIndex=3)

    # 删除指定表格
    ow.wordDeleteTable("doc.docx", TableIndex=2)

    # 删除指定表格行
    ow.wordDeleteTableRow("doc.docx", TableIndex=1, RowIndex=4)

    # 插入LaTeX公式
    latex_code = r"\frac{a}{b} = \sqrt{c}"
    ow.wordInsertLatexFormula("doc.docx", ParaIndex=5, LatexCode=latex_code, NewParagraph=True)

    # 使用parse_text_and_formula函数解析文本和公式
    text = "这是文本 $y=x^2+x+1$，还有公式 $$\\frac{a}{b}=c$$。"
    parsed = ow.parse_text_and_formula(text)
    for ttype, content in parsed:
        if ttype == TextType.Text:
            print("[文本]", content)
        else:
            print("[公式]", content)

---

备注与注意事项
==============

- 所有文件路径均支持相对和绝对路径，路径必须包含文件名及扩展名。
- 行列及索引均从1开始（段落索引除外，特定函数中段落索引为0开始）。
- Word表格中合并单元格影响行列索引的语义，请根据实际合并情况调整参数。
- 上标和下标文本的标记语法需严格使用英文括号：“^()” 表示上标，“_()” 表示下标。
- 对段落字体大小设置参数，需传入 `docx.shared.Pt` 或 `docx.shared.Length` 类型对象，示例中的数值为示意，使用时请注意转换。
- 插入LaTeX公式需要 `spire.doc` 库，安装及使用请参考官方文档。

联系我们
========

如遇任何问题或者功能建议，请通过下列方式联系作者：

- 称呼：王先生 (Name: Jhonie)
- E-mail: queenelsaofarendelle2022@gmail.com / 2570518164@qq.com
- QQ：2570518164

---

感谢使用 FreeWork 办公自动化工具包！欢迎反馈与交流。
