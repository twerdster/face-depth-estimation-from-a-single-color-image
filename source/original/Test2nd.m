

% The tif images in dataDir are depth images normalized between 0 and 65536
% or 0 and 256 depending on the bit depth
% This function assumes it is being run from the models folder. It wont
% work otherwise.
dataDir = '.\';
dataFile = 'DATATESTf13.mat';
outDir = [dataDir 'out1\'];
nFeatures = 100;
probeSize = 50000;
featurePrecision = 'int8';
maxFilesOpen = 500;
rseed = 0;


load('Calib_Results_stereo.mat','KK_left','KK_right','R','T','kc_left','kc_right');
T = T*26.6;
KK_left = KK_left/2;
KK_left(3,3) = 1;
K = KK_right;

load(dataFile);
DATA = DATA(1:500,:);
pred_vec = pred_vec(:,:,1:500);


warning off;
fclose all;

% Harcoded:
maxLabel = 8;
maxDiff = 200; %20cm
dataDir

nImages=size(DATA,1);

h = waitbar(0,'Calculating total number of samples ...');

depth = DATA{1,1};
maxD = max(depth(:));

totSamples = 0;
for i=1:nImages
    depth = (DATA{i,1});
    totSamples = totSamples + sum(depth(:)~=0);
    waitbar(i/nImages,h);
end

delete(h);


ISINT8 =        strcmp(lower(featurePrecision),'int8');
ISINT16 =       strcmp(lower(featurePrecision),'int16');
ISINT32 =       strcmp(lower(featurePrecision),'int32');
ISFLOAT32 =     strcmp(lower(featurePrecision),'single');

if ~ISINT8 & ~ISINT16 & ~ISINT32 & ~ISFLOAT32
    error('Unsupported bit depth.')
end

if ISINT8       featureMax = 127; end
if ISINT16      featureMax = 32767; end
if ISINT32      featureMax = 2147483500; end
if ISFLOAT32    featureMax = 3.3e+037; end

rand('seed',rseed);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     FEATURE COORDINATE GENERATOR                         %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
rot = @(P,dA)  [ cos(dA) -sin(dA); sin(dA) cos(dA)] * P;
expp=@(s,n) (exp(-s:s/(n-1):0)-exp(-s))/(1-exp(-s))

nDiv = 20;
steepness = 1.2;
radius = probeSize*(0:1/(nDiv):1);
radius = probeSize*expp(steepness,nDiv+1);
radius=radius/2;
radius = radius(randperm(nDiv)+1);
numRots = nFeatures/nDiv;
delta = 2*pi/numRots;


coords_ = [];
for i=1:nDiv
    dA = delta * (i-1)/double(nDiv) + rand(1)*delta*0.5;
    coords_ = [coords_ rot([0 radius(i)]',dA)];
end

coords = [];
for i=1:numRots
    dA = delta*i;
    coords = [coords rot(coords_,dA)];
end

coords = [coords; (rand(size(coords))-0.5)*0.1*probeSize];


plot(coords(1,:),coords(2,:),'r.');axis equal;hold on
plot(coords(3,:),coords(4,:),'g.');
hold off

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% We want Colors to exist in the directory this file is called from and not
% the folder where the images are.

fBase = 'F_';
bot = 1;
mkdir(outDir);
coordsFile = [outDir 'coords.co'];
labelFile = [outDir 'Labels.lbl'];
posesFile = [outDir 'Poses.pose'];
locationsFile = [outDir 'Locations.xyz'];
threshFile = [outDir 'Threshholds.thr'];


%I added this
%featurePrecision = double(featurePrecision);
featSize = totSamples*sizeof(featurePrecision);

% remove all data files
delete(locationsFile);
delete(coordsFile);
delete(labelFile);
delete(posesFile);
delete(threshFile);
delete([outDir '*.feat']);

coordsSize = (4*nFeatures)*sizeof('single');
labelSize = totSamples*sizeof('int8');
posesSize = totSamples*sizeof('int32');
locationsSize = totSamples*sizeof('single')*3;

system(['..\Contig\contig -n ' coordsFile ' ' num2str(coordsSize) ]);
system(['..\Contig\contig -n ' labelFile ' ' num2str(labelSize) ]);
system(['..\Contig\contig -n ' posesFile ' ' num2str(posesSize) ]);
system(['..\Contig\contig -n ' locationsFile ' ' num2str(locationsSize) ]);

fLabel=fopen(labelFile,'r+b');
fPose=fopen(posesFile,'r+b');
fLocations=fopen(locationsFile,'r+b');

depth = DATA{1,1};
fMin = [];
fMax = [];
Data = zeros(totSamples,nFeatures,featurePrecision);
Label1 = zeros(totSamples,1,'uint8');
while 1
    top = min(bot+maxFilesOpen-1,nFeatures);
    fprintf('\nGenerating features %i to %i ...\n',bot-1,top-1);
    
    Q = bot:top;
    imCnt=0;
    fileHandles = [];
    for feat = Q
        featFile = [outDir fBase num2str(feat-1,'%.4i') '.feat'];
        system(['..\Contig\contig -n ' featFile ' ' num2str(featSize) ]);
        fileHandles(feat) = fopen(featFile,'r+b');
        fMin(feat) = featureMax;
        fMax(feat) = -featureMax;
    end
    tic
    ofs = 1;
    for imageIndex = 1:nImages
        imCnt = imCnt+1;
        
        % Resave the label images so that they are real labels and not colors
        %label = pred_vec(:,:,imageIndex)-1;   %This is so that we start labels
        % from 0.
        
        
        % Resave the depth images. This is so that the datatype
        % matches and also so that we can use the images with opencv
        depth = DATA{imageIndex,1};
        
        % Now convert the depth image to its real value which we need in order
        % to calculate the depth normalized coordinates
        depth = double(depth);
        depth = medfilt2(depth,[5 5]);
        depth = single(depth);
        
        
        inds = int32(find(depth~=0));
        %inds = int32(find(label~=7));    % Find all indices of image that aren't
        % black background.
        
        
        % We need to process EXACTLY the same data points for each feature
        % batch that we process
        rand('seed',imageIndex + rseed);    % take random points for
        % each specific color.
        
        [i,j]=ind2sub(size(depth),inds);
        coords_ = single(coords(:,Q));
        
        xy1 = inv(K)*single([j'-1;i'-1;ones(1,length(j))]);
        XYZ = single(xy1.*repmat(depth(inds)',3,1));
        
        %needs to be compiled with mex getDepthFeatures.cpp COMPFLAGS="/openmp $COMPFLAGS"
        data = getDepthFeatures(i, j, depth, coords_, maxDiff, featureMax);
        Data(ofs:(length(inds)+ofs-1),:) = data;
       % labels = label(inds);
        
       % Label(ofs:(length(inds)+ofs-1)) = labels;
        
        ofs = ofs + length(inds);
        poses = ones(size(data,1),1)*(imageIndex-1);
        Data = double(Data);
       % Label = double(Label);
        
        pred = predict(treeClassifier, Data);
        pred1 = cellfun(@str2num, pred); %I added the 1's and 2's on the pred to make it easier to slide pred into pred_vec.
        Label1 = reshape(pred1,240, 320);
        imagesc(Label1,[0 7]); 
        drawnow

        
        %write data and labels to feature files
        for feat=Q
            f = feat-Q(1)+1;
            fwrite(fileHandles(feat),data(:,f),featurePrecision);
            ind = abs(data(:,f))~=featureMax;
            if all(~ind)
                continue;
            end
            fMin(feat) = min(fMin(feat),min(data(ind,f)));
            fMax(feat) = max(fMax(feat),max(data(ind,f)));
        end
        if Q(1) == 1 % We only need to run this once for the outer iteration
            fwrite(fLabel,labels,'uint8');
            fwrite(fPose, poses, 'uint32');
            fwrite(fLocations, XYZ(:), 'single');
        end
        if mod(imCnt,1) == 0
            toc
            tic;
            fprintf('Image %i / %i\n ',imageIndex,nImages);
            
            imshow(depth,[]);
            drawnow;
        end
        
    end
    for feat = Q
        fclose(fileHandles(feat));
    end
    
    %This is our end condition
    if Q(end) == nFeatures
        break;
    end
    bot = top + 1;
end

fclose(fLabel);
fclose(fPose);
fclose(fLocations);
%Write thresholds
writeDataThresholds(outDir,nFeatures,featurePrecision,featureMax,fBase,threshFile,fMin,fMax);

fCoords=fopen([outDir 'Coords.co'],'r+b');
fwrite(fCoords,coords,'single');
fclose(fCoords);















