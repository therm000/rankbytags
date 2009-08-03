
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <math.h>
#include <cmath>

using namespace std;

void Tokenize(const string& str,
                      vector<string>& tokens,
                      const string& delimiters = " ")
{
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);
    // Find first "non-delimiter".
    string::size_type pos     = str.find_first_of(delimiters, lastPos);

    while (string::npos != pos || string::npos != lastPos)
    {
        // Found a token, add it to the vector.
        tokens.push_back(str.substr(lastPos, pos - lastPos));
        // Skip delimiters.  Note the "not_of"
        lastPos = str.find_first_not_of(delimiters, pos);
        // Find next "non-delimiter"
        pos = str.find_first_of(delimiters, lastPos);
    }
}


class PageRank
{
public:
	double damping;
	string name;
	vector<string> nodes;
	vector<pair<string,string> > edges;
 	vector<vector<int> > outbound;
	vector<vector<int> > inbound;
/*
     public void snd_fst_cmp(A, B)
	{
         ret = A[1] - B[1]
         if ret < 0:
             return -1
         elif ret > 0:
             return 1
         else:         
             if A[0] > B[0]:
                 return -1
             elif A[0] < B[0]:
                 return 1
             else:
                 return 0
	}
  */

     PageRank(string name)
	{
		this->damping = 0.85;
		this->name = name;

		vector<string> nodes;
		vector<pair<string,string> > edges;
		
		string line;
		ifstream myfile (string("../data/" + name + ".nodes").c_str());


		if (myfile.is_open())
		{
			 while (! myfile.eof() )
			    {
			      getline (myfile,line);
			      if (line.size() == 0)
				break;
			      vector<string> tokens;
 			      Tokenize(line, tokens);
			      string A = tokens[0];
			      this->nodes.push_back(A);
			      //string B = tokens[1];
			      //cout << line << endl;
			    }
		    myfile.close();
		  }
		else cout << "Unable to open file"; 

		ifstream myfile2 (string("../data/" + name + ".edges").c_str());
		if (myfile2.is_open())
		{
			 while (! myfile2.eof() )
			    {
			      getline (myfile2,line);
			      if (line.size() == 0)
				break;
			      vector<string> tokens;
 			      Tokenize(line, tokens);
			      string A = tokens[0];
			      string B = tokens[1];
			      this->edges.push_back(pair<string,string>(A,B));			      
			      //cout << line << endl;
			    }
		    myfile2.close();
		  }
		else cout << "Unable to open file"; 


         // code into integers, to avoid use of dictionaries everywhere.
         //cout << "mapping nodes to integers" << endl;

	 map<string,int> map_node_int;
	 map<int,string> map_int_node;
	 for (int i=0; i < this->nodes.size(); i++) {
             string node = this->nodes[i];
             map_node_int[node] = i;
             map_int_node[i] = node;
	     }
    
	 for(int i=0; i < this->nodes.size(); i++) {
		this->outbound.push_back(vector<int>());
		this->inbound.push_back(vector<int>());
		}

         //cout << "extracting output neighbors per node" << endl;
	 for (int i=0; i < this->edges.size(); i++) {
	        int n1 = map_node_int[this->edges[i].first];
		int n2 = map_node_int[this->edges[i].second];
                this->inbound[n2].push_back(n1);
                this->outbound[n1].push_back(n2);
		}
   }
 
     vector<double> initial()
	{
		vector<double> ret;
		for (int i=0; i < this->nodes.size(); i++)
			ret.push_back(1.0/this->nodes.size());
		return ret;
	}

  std::vector<double>& sparse_multiply(std::vector<double>& vector, double convergence = 0.0001, int max_times = 85)
  {
          std::vector<int> sinks;
          for(int i=0;i < this->nodes.size();i++)
            if (this->outbound[i].size() == 0)
              sinks.push_back(i);
                
          int t = 0;
          double norm2 = 1.0;
	  double norm_inf = 1.0;
          while (t < max_times && norm_inf >= convergence)
            {
              //cout << "PageRank iteration #" << t << endl;
              //cout << "norm2: " << norm2 << " stop when less than " << convergence << endl;
    
              norm_inf = 0.0;
             
              // compute stochastic component
              double prod_scalar = 0.0;
              for (int s=0; s < sinks.size(); s++)
                {
                  prod_scalar += vector[sinks[s]] * this->damping;
                }
              prod_scalar += 1.0 - this->damping;

              //std::vector<double> stoch;
              //for (int i=0; i < this->nodes.size(); i++)
              //  stoch.push_back(prod_scalar/this->nodes.size());

              // do sparse matrix multip
              //std::vector<double> new_vector = stoch;
	      std::vector<double> new_vector = vector;
	      prod_scalar = prod_scalar/this->nodes.size();

              for (int k=0; k<vector.size(); k++){
                if (k%1000 == 0) {
                  //cout << "node " << k << " of " << vector.size() << " in iteration matrix mult" << endl;
                }
		new_vector[k] = prod_scalar;
                for (int r=0; r < this->inbound[k].size(); r++) {
                  int in_node = this->inbound[k][r];
                  new_vector[k] += (vector[in_node] / this->outbound[in_node].size()) * this->damping;
                }
		if (std::fabs(new_vector[k] - vector[k]) > norm_inf)
			norm_inf = std::fabs(new_vector[k] - vector[k]);
//                norm2 += (new_vector[k] - vector[k]) * (new_vector[k] - vector[k])             ;
              }

              t += 1;
  //            norm2 = sqrt(norm2) / this->nodes.size();
              vector = new_vector;
            }
	  cout << "iterations: " << t << endl;
          return vector; 
        }
 

  std::vector<pair<double,string> >& normalize(std::vector<pair<double,string> >& rank)
  {
    if (rank.size() == 0)
      return rank;
    double sum = 0.0;
    for (int i=0; i < rank.size(); i++)
        sum += rank[i].first;
    if (sum == 0.0)
      return rank;
    for (int i=0; i < rank.size(); i++)
      rank[i] = pair<double,string>(rank[i].first/sum, rank[i].second);
    return rank;
  }

  vector<pair<double,string> > ranking(double convergence=-1.0, int max_iterations=100)
  {
    if (this->nodes.size() == 0)
  return vector<pair<double,string> >();
  if (convergence == -1.0)
    convergence = 0.000001;
  vector<double> pagerank = this->initial();
  pagerank = this->sparse_multiply(pagerank, convergence, max_iterations);
  std::vector<pair<double,string> > new_pagerank;
  for (int i=0; i<this->nodes.size(); i++)
    new_pagerank.push_back(std::pair<double,string>(pagerank[i],this->nodes[i]));
  sort(new_pagerank.rbegin(),new_pagerank.rend());
  new_pagerank = PageRank::normalize(new_pagerank);

  //  for (int i = 0; i < new_pagerank.size(); i++)
  //  cout << new_pagerank[i].first << " " << new_pagerank[i].second << endl;

  return new_pagerank;

}

  void save_pagerank()
{
  vector<pair<double,string> > rank = this->ranking();

  ofstream myfile (string("../data/" + name + ".rank").c_str());
  if (myfile.is_open())
  {
    for (int i = 0; i < rank.size(); i++)
      myfile << scientific << rank[i].second << " " << rank[i].first << endl;
    myfile.close();
  }
  else cout << "Unable to open file";

}

};


int main( int argc, char *argv[] ) 
{
  PageRank pr(argv[1]);
  pr.save_pagerank();
  return 0;
}
