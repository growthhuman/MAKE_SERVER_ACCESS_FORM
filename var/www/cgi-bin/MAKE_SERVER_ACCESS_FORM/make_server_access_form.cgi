#!/usr/bin/perl

#-----#-----#-----MUST-----#-----#-----#
use strict;
use warnings;
use Encode 'decode';
use Encode 'encode';
use utf8;
#-----#-----#-----MUST-----#-----#-----#

# 00-色々準備
#
#-----#-----#----------------------------------------------------#-----#-----#
use Encode 'decode';
use CGI;
use CGI::Carp('fatalsToBrowser');
use Data::Dumper 'Dumper';#debug

my $q = CGI->new;
$q ->charset('UTF-8');
print $q ->header;
# 01-Define Variavles
#
#-----#-----#----------------------------------------------------#-----#-----#
my $person_csv_list = "$ARGV[0]";                   #引数で受け取ったファイルを、代入する。
#my $person_csv_list = "2013_0702_imabayashi.csv";  #引数で渡さずファイル名固定で行う場合
my $server_csv_list = './access.lst';               #サーバIPリストファイル場所指定
my $last_lines      = [];                           #最後に出力するための行のリファレンス
my $date            = `date +%Y%m%d`;
my @csv_array;
my @server_array;

# 02-ファイルのオープン
#
#-----#-----#----------------------------------------------------#-----#-----#
#open (my $person_list,'<',"$ARGV[0]");
open (my $person_list,'<',"2013_0702_imabayashi.csv");
open (my $server_list,'<','access.lst');

# 03-オープンしたファイルを配列に代入。
#
#-----#-----#----------------------------------------------------#-----#-----#
while (<$person_list>){
my $a = decode('Shift_JIS',$_);                     #Shift_JIS(csv)をデコードして内部文字列にする
push (@csv_array,$a);
}

while(<$server_list>){
push (@server_array,$_);
}

# 04-配列を二重ループで読み込んで、元となる情報の作成。
#
#-----#-----#----------------------------------------------------#-----#-----#
while (my $person = <@csv_array>) {
        my @rec = split(',',$person);
        while (my $server = <@server_array>) {

        my $last_line = {};                     #ハッシュに情報を入れ込む。
        $last_line->{flag}        = $rec[0];
        $last_line->{ip}           = $rec[1];
        $last_line->{division}     = $rec[2];
        $last_line->{company_name} = $rec[3];
        $last_line->{name}         = $rec[4];
        $last_line->{server}       = $server;

        push @$last_lines, $last_line; #$last_lineというハッシュを、$last_linesというレファレンスに格納
        };
};

# 05-整形して出力を行う。
# 1 新規 10.205.10.55 host ⇒ 10.200.21.91 host 申請部署 名前の形式で出力
#-----#-----#----------------------------------------------------#-----#-----#
my $number = 1;
foreach my $last_line (@$last_lines){
        next if ("$last_line->{ip}" =~ /^IP/); #IPが頭についたら、スキップ(CSVの行頭対策)
        print "$number"."\t";
        print "$last_line->{flag}"."\t";
        print "$last_line->{ip}"."\t";
        print "host"."\t";
        print "⇒"."\t";
        print "$last_line->{server}"."\t";
        print "host"."\t";
        print "$last_line->{division}"."\t";
        print "$last_line->{company_name}"."$last_line->{name}"."<br>";
        $number = "$number" + 1;
};

# 06-ファイルのクローズ
#
#-----#-----#----------------------------------------------------#-----#-----#
close $person_list;
close $server_list;
