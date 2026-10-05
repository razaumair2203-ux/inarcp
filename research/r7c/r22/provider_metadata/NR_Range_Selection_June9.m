% This calculation of the range bins and range axes should be transparent
% to the adcpredelay parameter because everything is relative to the direct
% breakthrough in passive nodes

function [Data_out,Range_Axis,Range_Bins] = NR_Range_Selection_June9(Data,T_stamp,Node,~) 


%% Phase Correction if needed for passive nodes

if Node == 2 || Node ==1
    
    %Find peak amplitude    
    [MaxVal, MaxRangeBin] = max(mean(abs(Data)));
    %Find phase angle from all pulses in the reference range gate and
    %replicate
    ReferencePhase=angle(Data(:,MaxRangeBin));
    ReferencePhase2=repmat(ReferencePhase,1,size(Data,2));
    %Remove phase from reference range gate
    CorrectPhase=angle(Data)-ReferencePhase2;
    Data=abs(Data).*exp(1i*CorrectPhase);
    disp(strcat('Phase Correction using range bin ',num2str(MaxRangeBin),'Node ', num2str(Node)))
end

%% Select Range bins with clutter patch for each dataset

if strcmp(T_stamp,'1113')
    
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (530:630); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=75; %Range bin of dir breakthrough
        N2_Range_Bins = (300:400); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (299:399); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
       
elseif strcmp(T_stamp,'1118')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (430:530); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=75; %Range bin of dir breakthrough
        N2_Range_Bins = (200:300); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (199:299); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
elseif strcmp(T_stamp,'1123') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (430:530); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=75; %Range bin of dir breakthrough
        N2_Range_Bins = (200:300); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (199:299); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
elseif strcmp(T_stamp,'1128')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (400:470); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=75; %Range bin of dir breakthrough
        N2_Range_Bins = (170:240); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (169:239); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
elseif strcmp(T_stamp,'1132')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (370:440); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=75; %Range bin of dir breakthrough
        N2_Range_Bins = (140:210); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (139:209); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
elseif strcmp(T_stamp,'1139')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (360:420); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=75; %Range bin of dir breakthrough
        N2_Range_Bins = (130:190); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (129:189); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
elseif strcmp(T_stamp,'1146')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (330:380); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=75; %Range bin of dir breakthrough
        N2_Range_Bins = (100:150); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (99:149); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
   
 elseif strcmp(T_stamp,'1239')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (531:631); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=74; %Range bin of dir breakthrough
        N2_Range_Bins = (300:400); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (300:400); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
        
 elseif strcmp(T_stamp,'1243')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (431:531); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=74; %Range bin of dir breakthrough
        N2_Range_Bins = (200:300); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (200:300); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end 
     
 elseif strcmp(T_stamp,'1247')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (391:471); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=74; %Range bin of dir breakthrough
        N2_Range_Bins = (160:240); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (160:240); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
 elseif strcmp(T_stamp,'1251')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (381:451); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=74; %Range bin of dir breakthrough
        N2_Range_Bins = (150:220); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (150:220); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
     
 elseif strcmp(T_stamp,'1254')
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (381:451); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=74; %Range bin of dir breakthrough
        N2_Range_Bins = (150:210); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (150:210); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
     
 elseif strcmp(T_stamp,'1258')
     if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (351:411); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=74; %Range bin of dir breakthrough
        N2_Range_Bins = (120:180); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (120:180); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end 
     
 elseif strcmp(T_stamp,'1302')       
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (331:361); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=74; %Range bin of dir breakthrough
        N2_Range_Bins = (100:130); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (100:130); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
    elseif strcmp(T_stamp,'1446') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (541:641); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=64; %Range bin of dir breakthrough
        N2_Range_Bins = (300:400); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (310:410); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
    
    elseif strcmp(T_stamp,'1450') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (441:541); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=64; %Range bin of dir breakthrough
        N2_Range_Bins = (200:300); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (210:310); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
        
    elseif strcmp(T_stamp,'1457') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (401:481); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=64; %Range bin of dir breakthrough
        N2_Range_Bins = (160:240); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (170:250); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end     
        
    elseif strcmp(T_stamp,'1501') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (391:461); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=64; %Range bin of dir breakthrough
        N2_Range_Bins = (150:220); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (160:230); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end  
        
    elseif strcmp(T_stamp,'1508') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (381:441); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=64; %Range bin of dir breakthrough
        N2_Range_Bins = (140:200); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (150:210); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
        
    elseif strcmp(T_stamp,'1512') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (361:401); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=64; %Range bin of dir breakthrough
        N2_Range_Bins = (120:160); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (130:170); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end      
        
    elseif strcmp(T_stamp,'1518') 
    if Node == 3
        RBinZeroN3=62; %Zero of the node
        N3_Range_Bins = (321:361); %Bins with clutter cell
        N3_Range_Axis = (N3_Range_Bins).*6;    
        Data_out=Data(:,N3_Range_Bins);
        Range_Axis=N3_Range_Axis;
        Range_Bins=N3_Range_Bins;
        
    elseif Node == 2
        RBinZeroN2=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N2=64; %Range bin of dir breakthrough
        N2_Range_Bins = (80:120); %Bins with clutter cell
        N2_Range_Axis = baseline+((N2_Range_Bins-dirbrkthr_N2).*6);    
        Data_out=Data(:,N2_Range_Bins);
        Range_Axis=N2_Range_Axis;
        Range_Bins=N2_Range_Bins;
        
    elseif Node == 1
        RBinZeroN1=62; %Zero of the node
        baseline=1830; %in m
        dirbrkthr_N1=74; %Range bin of dir breakthrough
        N1_Range_Bins = (90:130); %Bins with clutter cell
        N1_Range_Axis = baseline+((N1_Range_Bins-dirbrkthr_N1).*6);    
        Data_out=Data(:,N1_Range_Bins);
        Range_Axis=N1_Range_Axis;
        Range_Bins=N1_Range_Bins;      
    end
end



