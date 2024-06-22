# ms_pdf_title_parser
Microsoft Learn PDF Document Parser


微軟的 Learn 網站提供了大量的文件, 同時也包含了 Pdf 的版本可以直接下載。
然而, Adobe 的 Reader 在閱讀此類的檔案時非常得不方便。

例如, 當你點取文件中的連結的時候, 它會帶你到另一個頁面, 但似乎無法返回原始
的頁面, 使得在閱讀上很不連貫。

同時, 由於文件非常得大, 但 Adobe Reader 的 TOC 目錄索引似乎沒有細節。並且
在過大的文件中變得很不方便來回參考相關的連結內容。再者, 我希望能更全面地檢
閱文件包含了哪些主要的內容, 並且很快地找到該頁面所在的位置。

因此這個程式 (參考 parse_pdf_bulletpt.py) 主要在將從 微軟的 Learn 網站提
供的 PDF 文件, 用 Python 和相依的程式庫 (參考 requirements.txt) 將它解析
成一個包含了 TOC 目錄索引和頁面中的標題的頁碼的文件檔 (如 *.txt 檔案), 因此
我就可以同時打開 PDF reader 和這個索引檔, 快速地依上面指引的頁碼, 找到 PDF
對應的頁數, 然後在螢幕上交互參照。

注意: 由於 PDF 檔案時常變動並且檔案很大, 因此沒有包含在這個 repo 裡。請參考
(tree_list.txt) 裡的目錄結構, 把 pdf 原始檔案, 放在對應的資料夾中。
