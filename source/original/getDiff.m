function [diffMat, class] = getDiff(D, CM)

diffMat = [];
class = [];

[x,y] = find(D);
coords_x = 21;
coords_y = 35;
%diffMat = zeros(n,n);
for m = 1:length(x)
     diffMat_ = [];
    for i = ceil(-coords_x/2):floor(coords_x/2)
        for j = ceil(-coords_y/2):floor(coords_y/2)
            a = i + floor(coords_x/2) + 1;
            b = j + floor(coords_y/2) + 1;
            if (x(m)+i<1||y(m)+j<1||x(m)+i>size(D,1)||y(m)+j>size(D,2))
                diffMat_(a,b) = 0;
            else
                diffMat_(a,b) = D(x(m)+i,y(m)+j) - D(x(m),y(m));
            end
        end
    end
 %  diffMat = [diffMat,diffMat_];
    diffMat = vertcat(diffMat,diffMat_);
        class = [class;ones(size(diffMat_,1),1)*CM(x(m),y(m))];
end
end
