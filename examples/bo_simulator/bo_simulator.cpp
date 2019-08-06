#include "../../include/boat.hpp"

#include <iostream>
#include <fstream>
#include <string>

using namespace std;

using boat::RangeParameter;
using boat::CategoricalParameter;

using boat::GPParams;
using boat::ProbEngine;
using boat::SemiParametricModel;
using boat::DAGModel;
using boat::NLOpt;
using boat::BayesOpt;
using boat::generator;

// Arrays of actual values for categorical parameters
const int cache_size_values[] = {16384, 32768, 65536, 131072};

// results file name
const string sim_results_file = "results.csv";

// Parameters for the model
struct AladdinParams{
  AladdinParams() :
    cycle_time_(1, 6),
    pipelining_(0, 2),
    tlb_hit_latency_(1, 5), 
    cache_size_(0, 4){}  // Categorical parameter

  RangeParameter<int> cycle_time_;
  RangeParameter<int> pipelining_;
  RangeParameter<int> tlb_hit_latency_;
  RangeParameter<int> cache_size_;
};

// Prepares a string line defining parameters for the simulator
std::string prep_simulator_params(const AladdinParams &p) {

  std::string sim_params = "{";

  sim_params += "'cycle_time': " + std::to_string(p.cycle_time_.value()) + ",";
  sim_params += "'pipelining': " + std::to_string(p.pipelining_.value()) + ",";
  sim_params += "'tlb_hit_latency': " + std::to_string(p.tlb_hit_latency_.value()) + ",";

  // getting the categorical parameter values
  sim_params += "'cache_size': " + std::to_string(cache_size_values[p.cache_size_.value()]) + ",";

  sim_params += "}";

  return sim_params;
}

// Creates the header line for the results file and writes in sim_results_file
void results_header() {
    ofstream results_file (sim_results_file);

    if (results_file.is_open()) {

      results_file << "cycle_time" << "," << "pipelining" << "," << "tlb_hit_latency" << ","<< "cache_size" << ","<< "result" << std::endl;
      results_file.close();
    }
}

// Saves the input parameters and the resulting value of the objective function into a file
void append_results(const AladdinParams &p, double result) {
  ofstream results_file(sim_results_file, ios::out | ios::app);

  if (results_file.is_open()) {

    results_file << std::to_string(p.cycle_time_.value()) + ",";
    results_file << std::to_string(p.pipelining_.value()) + ",";
    results_file << std::to_string(p.tlb_hit_latency_.value()) + ",";
    results_file << std::to_string(cache_size_values[p.cache_size_.value()]) + ",";
    results_file << std::to_string(result);
    results_file << std::endl;

    results_file.close();
  }
}

// Reads in the result from simulator benchmark run
double read_simulator_result(const std::string results_file) {

  std::string sim_value;
  double sim_result = 0.0;

  ifstream myfile(results_file);

  // We expect only one value to be saved in the results file.
  if (myfile.is_open()) {
			myfile >> sim_value;

    sim_result = std::stod(sim_value);
	}

	return sim_result;
}

// Objective function
// At the moment this is very ugly implementation but just to get it working.
// TODO: implement in a more efficient fasion
double run_simulator(const AladdinParams &p) {

  std::string command = "python ";

  const std::string python_file = "simulator.py";
  const std::string results_file = "gem5_sim_res.txt";

  // main python script to run the simulator
  command += python_file;
  command += " ";
  command += '"';

  // set the parameters for the simulator
  command += prep_simulator_params(p);

  command += '"';

  // setting the objective p
  command += " ";
  command += "P1";

  std::cout << command << "\n";

  // run the simulator
  system(command.c_str());

  // retrieve result
  double result = read_simulator_result(results_file);

  // saving results into a file
  append_results(p, result);

  // TODO: delete the results file from the simulator.

  return result;
}

/// Naive way of optimizing it, model with simple GP prior
struct Param : public SemiParametricModel<Param> {
  Param() {
    p_.default_noise(0.1);

    // Ranges require updating with more realistic values from the results
    p_.mean(uniform_real_distribution<>(0.0, 1.5)(generator));
    p_.stdev(uniform_real_distribution<>(0.0, 1.5)(generator));

    // the length scale of each dimension of the input
    p_.linear_scales({
      uniform_real_distribution<>(1.0, 6.0)(generator), // cycle_time
      uniform_real_distribution<>(0.0, 2.0)(generator), // pipelining
      uniform_real_distribution<>(1.0, 5.0)(generator), // tbl_hit_latency
      uniform_real_distribution<>(0.0, 4.0)(generator) // cache_size (categorical)
      }); 

    set_params(p_);
  }

  GPParams p_;
};

struct FullModel : public DAGModel<FullModel> {

  // for a semi parametric model
  FullModel(){
    eng_.set_num_particles(10000);
  }

  // registers objective under graph
  void model(const AladdinParams& p) {
    output("objective", eng_, 
      p.cycle_time_.value(), 
      p.pipelining_.value(), 
      p.tlb_hit_latency_.value(),
      p.cache_size_.value()
      );
  }

  void print() {
    PR(AVG_PROP(eng_, p_.mean()));
    PR(AVG_PROP(eng_, p_.stdev()));
    PR(AVG_PROP(eng_, p_.linear_scales()[0]));
    PR(AVG_PROP(eng_, p_.linear_scales()[1]));
  }

  ProbEngine<Param> eng_;
};

// what is the next point we should test
// incumbent - best current example
void maximize_ei(FullModel& m, AladdinParams& p, double incumbent) {

  NLOpt<> opt(
    p.cycle_time_, 
    p.pipelining_, 
    p.tlb_hit_latency_,
    p.cache_size_
    );

  // finds high uncertainty points
  // r - expected improvement
  auto obj = [&]() {
    double r = m.expected_improvement("objective", incumbent, p);
    std::cout << "expected_improvement: " << r << std::endl;
    return r;
  };

  opt.set_objective_function(obj);
  opt.set_max_num_iterations(1000);
  opt.set_maximizing();
  opt.run_optimization();
}

void bo_naive_optim() {

  results_header();

  FullModel m;
  m.set_num_particles(10000);

  AladdinParams p;
  BayesOpt<unordered_map<string, double> > opt;

  auto subopt = [&]() {
    maximize_ei(m, p, opt.best_objective());
  };

  auto util = [&]() {
    unordered_map<string, double> res;

    res["objective"] = run_simulator(p);

    PR(
      p.cycle_time_.value(), 
      p.pipelining_.value(), 
      p.tlb_hit_latency_.value(), 
      p.cache_size_.value(),
      res["objective"]);

    return res;
  };

  auto learn = [&](const unordered_map<string, double>& r){
    m.observe(r, p);
  };

  opt.set_subopt_function(subopt);

  opt.set_objective_function(util);
  opt.set_learning_function(learn);

  opt.set_maximizing();
  opt.set_max_num_iterations(20);
  opt.run_optimization();
}

int main() {
  bo_naive_optim();
}
