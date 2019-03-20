#include "../../include/boat.hpp"

using namespace std;

using boat::RangeParameter;
using boat::GPParams;
using boat::ProbEngine;
using boat::SemiParametricModel;
using boat::DAGModel;
using boat::NLOpt;
using boat::BayesOpt;
using boat::generator;

// Parameters for the model
struct AladdinParams{
  AladdinParams() :
    cycle_time_(1, 6),
    cache_bandwidth_(4, 17){} // needs to be checked if this is the correct syntax

  RangeParameter<double> cycle_time_;
  RangeParameter<double> cache_bandwidth_;
};

// Objective function
// At the moment this is very ugly implementatio but just to get it working.
// TODO: implement in a more efficient fasion
double run_simulator(const AladdinParams &p) {

  std::string command = "python ",
              python_file = "simulator.py";

  double result = 0.0;


  // create a new input file

  command += "";

  // run run_simulator
  system(command.c_str());

  // retrieve result

  // delete input and output files


  return result;
}

/// Naive way of optimizing it, model with simple GP prior
struct Param : public SemiParametricModel<Param> {
  Param() {
    p_.default_noise(0.0);

    // Ranges require updating with more realistic values from the results
    p_.mean(uniform_real_distribution<>(0.0, 100.0)(generator));
    p_.stdev(uniform_real_distribution<>(0.0, 200.0)(generator));

    // the length scale of each dimension of the input
    p_.linear_scales({uniform_real_distribution<>(1.0, 6.0)(generator),
                     uniform_real_distribution<>(0.0, 15.0)(generator)}); // change for the pipelining_

    // for a categorical params needs to be investigated
    set_params(p_);
  }

  GPParams p_;
};

struct FullModel : public DAGModel<FullModel> {

  // for a semi parametric model
  FullModel(){
    eng_.set_num_particles(100);
  }

  // registers objective under graph
  void model(const AladdinParams& p) {
    output("objective", eng_, p.cycle_time_.value(), p.cache_bandwidth_.value());
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
  NLOpt<> opt(p.cycle_time_, p.cache_bandwidth_);

  // finds high uncertainty points
  // r - expected improvement
  auto obj = [&]() {
    double r = m.expected_improvement("objective", incumbent, p);
    return r;
  };

  opt.set_objective_function(obj);
  opt.set_max_num_iterations(10000);
  opt.set_maximizing();
  opt.run_optimization();
}

void bo_naive_optim() {
  FullModel m;
  m.set_num_particles(100);

  AladdinParams p;
  BayesOpt<unordered_map<string, double> > opt;

  auto subopt = [&]() {
    maximize_ei(m, p, opt.best_objective());
  };

  auto util = [&](){
    unordered_map<string, double> res;

    res["objective"] = run_simulator(p);

    PR(p.cycle_time_.value(), p.cache_bandwidth_.value(), res["objective"]);
    return res;
  };

  // takes the result
  auto learn = [&](const unordered_map<string, double>& r){
    m.observe(r, p);
  };

  opt.set_subopt_function(subopt);

  opt.set_objective_function(util);
  opt.set_learning_function(learn);

  opt.set_minimizing();
  opt.set_max_num_iterations(25);
  opt.run_optimization();
}

int main() {
  bo_naive_optim();
}
