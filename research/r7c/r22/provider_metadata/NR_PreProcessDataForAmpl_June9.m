clear all;
clc
%% Sea Clutter RSA 2011 - June 9

for D_set = 1 %1:21;
% D_set = 1; 
% Selection of the dataset from the folder

if D_set == 1;
%%%%% Data 1113
    N3_Data_file = 'e11_06_09_1113_58_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1113_58_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1113_58_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1113';
%     Pol = 'H';

elseif D_set == 2; 
%%%% Data 1118
    N3_Data_file = 'e11_06_09_1118_34_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1118_34_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1118_34_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1118';

elseif D_set == 3;
%%%% Data 1123
    N3_Data_file = 'e11_06_09_1123_49_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1123_49_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1123_49_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1123';
    
elseif D_set == 4;
%%%% Data 1128
    N3_Data_file = 'e11_06_09_1128_12_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1128_12_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1128_12_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1128';
    
elseif D_set == 5;
%%%% Data 1132
    N3_Data_file = 'e11_06_09_1132_56_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1132_56_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1132_56_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1132';
    
elseif D_set == 6;
%%%% Data 1139
    N3_Data_file = 'e11_06_09_1139_49_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1139_49_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1139_49_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1139';
    
elseif D_set == 7;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1146_48_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1146_48_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1146_48_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1146';
    
elseif D_set == 8;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1239_13_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1239_13_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1239_13_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1239';
    
elseif D_set == 9;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1243_26_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1243_26_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1243_26_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1243';
    
elseif D_set == 10;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1247_17_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1247_17_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1247_17_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1247';
    
elseif D_set == 11;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1251_05_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1251_05_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1251_05_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1251';
    
elseif D_set == 12;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1254_40_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1254_40_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1254_40_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1254';

elseif D_set == 13;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1258_56_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1258_56_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1258_56_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1258';
    
elseif D_set == 14;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1302_53_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1302_53_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1302_53_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1302';
    
    elseif D_set == 15;
%%%% Data 1446
    N3_Data_file = 'e11_06_09_1446_21_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1446_21_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1446_21_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1446';
    
    elseif D_set == 16;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1450_16_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1450_16_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1450_16_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1450';
    
    elseif D_set == 17;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1457_22_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1457_22_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1457_22_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1457';
    
    elseif D_set == 18;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1501_53_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1501_53_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1501_53_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1501';
    
    elseif D_set == 19;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1508_24_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1508_24_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1508_24_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1508';
    
    elseif D_set == 20;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1512_14_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1512_14_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1512_14_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1512';
    
    elseif D_set == 21;
%%%% Data 1146
    N3_Data_file = 'e11_06_09_1518_58_P1_1_130000_S0_1_2047_node3_MF_refsig';
    N2_Data_file = 'e11_06_09_1518_58_P1_1_130000_S0_1_2047_node2_MF_refsig';
    N1_Data_file = 'e11_06_09_1518_58_P1_1_130000_S0_1_2047_node1_MF_refsig';
    Dataset = '1518';
end

T_stamp = N2_Data_file(11:14);
N1_Node = str2num(N1_Data_file(45));
N2_Node = str2num(N2_Data_file(45));
N3_Node = str2num(N3_Data_file(45));
PRF = 1e3;

%% Load RTI data and call function to select range bins with clutter patch
dirN1='M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\N1\';
dirN2='M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\N2\';
dirN3='M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\N3\';

% Load N3 data
load(strcat(dirN3,N3_Data_file));%run(strcat(dirN3,N3_Data_file(1:end-10),'.m'));
Data_matched_N3=abs(Data_matched).^2/50; %Conversion to power
[Data_matched_N3,Range_axis_N3,Range_Bins_N3] = NR_Range_Selection_June9(Data_matched_N3,T_stamp,N3_Node);

% Load N2 data
load(strcat(dirN2,N2_Data_file));%run(strcat(dirN2,N2_Data_file(1:end-10),'.m'));
Data_matched_N2=abs(Data_matched).^2/50; %Conversion to power
[Data_matched_N2,Range_axis_N2,Range_Bins_N2] = NR_Range_Selection_June9(Data_matched_N2,T_stamp,N2_Node);

% Load N1 data
load(strcat(dirN1,N1_Data_file));%run(strcat(dirN1,N1_Data_file(1:end-10),'.m'));
Data_matched_N1=abs(Data_matched).^2/50; %Conversion to power
[Data_matched_N1,Range_axis_N1,Range_Bins_N1] = NR_Range_Selection_June9(Data_matched_N1,T_stamp,N1_Node);
clear Data_matched


 %% Need Wi-Fi Cleaning

% This part check for interference peaks in the average Power vs Time profile 
% and remove the pulses with a peak higher than a threshold
% Lots of if-s here to have a different threshold per dataset!!

if T_stamp == '1118'
    Threshold=10; %Thresholds in dB to remove WiFi 
elseif T_stamp == '1139' 
    Threshold=13;
elseif T_stamp == '1146' 
    Threshold=2;
elseif T_stamp == '1243' 
    Threshold=12;
elseif T_stamp == '1247' 
    Threshold=13;
elseif T_stamp == '1251' 
    Threshold=10;
elseif T_stamp == '1254' 
    Threshold=12;
elseif T_stamp == '1258' 
    Threshold=15;
elseif T_stamp == '1302' 
    Threshold=6;
elseif T_stamp == '1446' 
    Threshold=15;
elseif T_stamp == '1450' 
    Threshold=10;
elseif T_stamp == '1457' 
    Threshold=12;
elseif T_stamp == '1501' 
    Threshold=9;
elseif T_stamp == '1508' 
    Threshold=10;
elseif T_stamp == '1512' 
    Threshold=7;
elseif T_stamp == '1518' 
    Threshold=1;
else
    Threshold=23;
end

Data_Cell_ForProc={Data_matched_N2,Data_matched_N1};
for k=1:size(Data_Cell_ForProc,2)

Data_test=Data_Cell_ForProc{1,k};
    
meantest=mean(abs(Data_test),2);
if (strcmp(T_stamp,'1146') || strcmp(T_stamp,'1247')) && (k == 2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-10);
elseif (strcmp(T_stamp,'1254') && k==2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-6);
elseif (strcmp(T_stamp,'1258') && k==2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-3);
elseif (strcmp(T_stamp,'1446') && k==2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-5);
elseif (strcmp(T_stamp,'1501') && k==2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-11);
elseif (strcmp(T_stamp,'1508') && k==2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-5);
elseif (strcmp(T_stamp,'1512') && k==2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-8);
elseif (strcmp(T_stamp,'1518') && k==2)
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold-5);
else
    [r,c] =  find(10*log10(abs(meantest)./max(abs(meantest))) > -Threshold);

end
Data_test2=Data_test;
Data_test2(r,:)=0;

Data_Cell_ForProc{1,k}=Data_test2;
Data_Cell_ForProc{1,k}=Data_Cell_ForProc{1,k}(any(Data_Cell_ForProc{1,k},2),:);
end
Data_matched_N2=Data_Cell_ForProc{1,1}; Data_matched_N1=Data_Cell_ForProc{1,2};
clear Data_Cell_ForProc Data_test Data_test2


% %% Just a test to use not the power but the actual intensity
% 
% Data_matched_N3=(Data_matched_N3*50).^1/2;
% Data_matched_N2=(Data_matched_N2*50).^1/2;
% Data_matched_N1=(Data_matched_N1*50).^1/2;

N1pulses=size(Data_matched_N1,1); N2pulses=size(Data_matched_N2,1); N3pulses=size(Data_matched_N3,1);


%% Plot RTI and Doppler and save figures as png files

%Define the axis
Time_axis_N3=[1:N3pulses]./PRF; Time_axis_N2=[1:N2pulses]./PRF; Time_axis_N1=[1:N1pulses]./PRF;
Doppler_axis_N3=(-N3pulses/2:N3pulses/2-1)*(PRF)/N3pulses;
Doppler_axis_N2=(-N2pulses/2:N2pulses/2-1)*(PRF)/N2pulses;
Doppler_axis_N1=(-N1pulses/2:N1pulses/2-1)*(PRF)/N1pulses;

figure; %subplot(211)
imagesc(Range_axis_N3,Time_axis_N3,10*log10(Data_matched_N3./max(Data_matched_N3(:))),[-45 0])
title(strcat('RTI at N3 - ',T_stamp),'FontSize',14);colorbar;set(gca,'FontSize',14)
xlabel('Two way range [m]','FontSize',14);ylabel('Time [s]','FontSize',14) 
% subplot(212)
% imagesc(Range_axis_N3,Doppler_axis_N3,10*log10(abs(Data_doppler_N3./max(Data_doppler_N3(:)))),[-50 0])
% axis xy;colorbar;set(gca,'FontSize',14)
% title(strcat('Range-Doppler at N3 - ',T_stamp),'FontSize',14);
% xlabel('Two way range [m]','FontSize',14);ylabel('Doppler [Hz]','FontSize',14) 
saveas(gcf,['M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\','RTI N3-',N3_Data_file(11:14),'.png']) 

figure; %subplot(211)
imagesc(Range_axis_N2,Time_axis_N2,10*log10(Data_matched_N2./max(Data_matched_N2(:))),[-45 0])
title(strcat('RTI at N2 - ',T_stamp),'FontSize',14);colorbar;set(gca,'FontSize',14)
xlabel('Two way range [m]','FontSize',14);ylabel('Time [s]','FontSize',14) 
% subplot(212)
% imagesc(Range_axis_N2,Doppler_axis_N2,10*log10(abs(Data_doppler_N2./max(Data_doppler_N2(:)))),[-50 0])
% axis xy;colorbar;set(gca,'FontSize',14)
% title(strcat('Range-Doppler at N2 - ',T_stamp),'FontSize',14);
% xlabel('Two way range [m]','FontSize',14);ylabel('Doppler [Hz]','FontSize',14) 
saveas(gcf,['M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\','RTI N2-',N2_Data_file(11:14),'.png']) 

figure; %subplot(211)
imagesc(Range_axis_N1,Time_axis_N1,10*log10(Data_matched_N1./max(Data_matched_N1(:))),[-45 0])
title(strcat('RTI at N1 - ',T_stamp),'FontSize',14);colorbar;set(gca,'FontSize',14)
xlabel('Two way range [m]','FontSize',14);ylabel('Time [s]','FontSize',14) 
% subplot(212)
% imagesc(Range_axis_N1,Doppler_axis_N1,10*log10(abs(Data_doppler_N1./max(Data_doppler_N1(:)))),[-50 0])
% axis xy;colorbar;set(gca,'FontSize',14)
% title(strcat('Range-Doppler at N1 - ',T_stamp),'FontSize',14);
% xlabel('Two way range [m]','FontSize',14);ylabel('Doppler [Hz]','FontSize',14) 
saveas(gcf,['M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\','RTI N1-',N1_Data_file(11:14),'.png']) 

close all

% We may think at later stage to save the data as single to save space!!!!

save (strcat('M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\RTI_Node3_',T_stamp,'.mat'), 'Data_matched_N3','Range_axis_N3','Range_Bins_N3', '-v7.3');
save (strcat('M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\RTI_Node2_',T_stamp,'.mat'), 'Data_matched_N2','Range_axis_N2','Range_Bins_N1', '-v7.3');
save (strcat('M:\ewi\me\MS3\Francesco Fioranelli\DatiSeaClutterNapoli\RTI_Node1_',T_stamp,'.mat'), 'Data_matched_N1','Range_axis_N2','Range_Bins_N1', '-v7.3');

end




