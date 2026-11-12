
load DATATESTf1;

diffMat = [];
class = [];


for i = 1:502
  
    D = DATA{i,1};
    D(isnan(D)) = 0;
    
    CM = pred_vec(:,:,i);
    
[diffMat_, class_] = getDiff(D, CM);
diffMat = [diffMat;diffMat_];
class = [class;class_];

end

treeClassifier = TreeBagger(10, diffMat, class, 'oobpred', 'on');
save Tree_RGB2Labelb1.mat treeClassifier
save testb1.mat
