#!/usr/bin/perl

#======================================================================
# Name:     WWWUPL
# Version:  Ver2.13
# Category: フリーソフト（使用・改造・再配布自由）
# Contact:  http://tohoho.wakusei.ne.jp/
# Copyrignt (C) 1997-2004 杜甫々
#======================================================================

#
# 使用方法
#
# (1) 通常のCGIとして設置してください。(CGI設置の知識を必要とします)
# (2) wwwupl.cgiの隣にwwwuplディレクトリ($upload_dirで変更可能)を作成
#     してください。wwwuplディレクトリは、WEBサーバーが書き込めるよう
#     な権限(パーミッション)を設定してください。
# (3) HTMLファイルから以下のように呼び出してください。
#      <FORM METHOD=POST ENCTYPE="multipart/form-data" ACTION="wwwupl.cgi">
#      <INPUT TYPE=file NAME="AAA"><BR>
#      <INPUT TYPE=file NAME="BBB"><BR>   ←省略可
#      <INPUT TYPE=submit VALUE="送信">
#      </FORM>
# (4) アップロードされたファイルは、wwwuplディレクトリに、$append_suffix
#     で指定した拡張子付きで保存されます。$append_suffixを""にすると、
#     閲覧者が勝手に .cgi や .shtml のファイルを作成できてしまうので、
#     セキュリティには充分注意してください。
# (5) 読み込んだデータをすべて、連続バッファに読み込むので、あまり大きな
#     ファイルは転送できないかもしれません。
# (6) 16個以上同時にアップロードすることはできません。
#
# 履歴
#  1999/02/07 Ver2.00 初版
#  1999/02/14 Ver2.01 \r\nを含むバイナリ受信が失敗するバグを修正
#  1999/04/25 Ver2.02 ファイル名空欄時、form-data.uplができるバグを修正
#  1999/04/25 Ver2.10 TYPE=textなどのデータも受信できるようにした
#  1999/06/02 Ver2.11 muleのperl-mode対応 /(...$)/ -> /(...)$/
#  2001/05/09 Ver2.12 説明文の変更など
#  2004/04/04 Ver2.13 通信エラー時に無限ループの可能性がある問題を修正

# カスタマイズパラメータ
$upload_dir = "./PERSON_IP_LIST";  # アップロードファイルを格納するディレクトリ
#$append_suffix = ".upl"; # ファイル名に追加する拡張子

# ページヘッダを書き出す
print "Content-type: text/html\n";
print "\n";
print "<html>\n";
print "<head>\n";
print "<title>ファイルアップロード</title>\n";
print "</head>\n";
print "<body>\n";
print "<h2>ファイルアップロード</h2>\n";
print "<hr>\n";
print "<p>下記のファイルを受け取りました。</p>\n";
print "<ul>\n";

# 標準入力からデータを読みだす
$buf = "";
$read_data = "";
$remain = $ENV{'CONTENT_LENGTH'};
binmode(STDIN);
while ($remain) {
  $len = sysread(STDIN, $buf, $remain);
  if (!$len) {
    last;
  }
  $remain -= $len;
  $read_data .= $buf;
}

# データを解釈する
$pos1 = 0; # ヘッダ部の先頭
$pos2 = 0; # ボディ部の先頭
$pos3 = 0; # ボディ部の終端
$delimiter = "";
$max_count = 0;
while (1) {

  # ヘッダ処理
  $pos2 = index($read_data, "\r\n\r\n", $pos1) + 4;
  @headers = split("\r\n", substr($read_data, $pos1, $pos2 - $pos1));
  $filename = "";
  $name = "";
  foreach (@headers) {
    if ($delimiter eq "") {
      $delimiter = $_;
    } elsif (/^Content-Disposition: ([^;]*); name="([^;]*)"; filename="([^;]*)"/i) {
      if ($3) {
        $filename = $3;
        if ($filename =~ /([^\\\/]+)$/) {
          $filename = $1;
        }
      }
    } elsif (/^Content-Disposition: ([^;]*); name="([^;]*)"/i) {
      $name = $2;
    }
  }

  # ボディ処理
  $pos3 = index($read_data, "\r\n$delimiter", $pos2);
  $size = $pos3 - $pos2;
  if ($filename) {
    print "<li>FILE: " . html($filename) . "($size Byte)\n";
    if (open(OUT, "> $upload_dir/$filename")) {
      binmode(OUT);
      print OUT substr($read_data, $pos2, $size);
      close(OUT);
    }
  } elsif ($name) {
    $FORM{$name} = substr($read_data, $pos2, $size);
    print "<li>DATA: $name=" . html($FORM{$name}) . "\n";
  }

  # 終了処理
  $pos1 = $pos3 + length("\r\n$delimiter");
  if (substr($read_data, $pos1, 4) eq "--\r\n") {
    # すべてのファイルの終端
    last;
  } else {
    # 次のファイルを読み出す
    $pos1 += 2;
    if ($max_count++ > 16) { last; }
    next;
  }
}

# ページフッタを書き出す
print "</ul>\n";
print "<hr>\n";
print "<div><a href=./make_server_access_form.cgi?$upload_dir/$filename target='migi'>作成・出力</a></div>\n";
#print '<div><a href=./make_server_access_form.cgi "$upload_dir/$filename" >作成[戻る]</a></div>\n';
print "<div><a href=\"$ENV{'HTTP_REFERER'}\">[戻る]</a></div>\n";
print "</body>\n";
print "</html>\n";

sub html {
  local($msg) = @_;
  $msg =~ s/&/&amp;/g;
  $msg =~ s/</&lt;/g;
  $msg =~ s/>/&gt;/g;
  return $msg;
}
