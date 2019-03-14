#include "../../include/boat.hpp"

using namespace std;

using boat::ProbEngine;
using boat::SemiParametricModel;
using boat::DAGModel;
using boat::GPParams;
using boat::NLOpt;
using boat::BayesOpt;
using boat::SimpleOpt;
using boat::generator;
using boat::RangeParameter;

struct AladdinParams{
  AladdinParams() : cycle_time_(1, 6),
    pipelining_(0, 1){} // vector of values
  RangeParameter<double> cycle_time_;
  CategoricalParameter<int> pipelining_;
};

// Objective function
double run_simulator(const AladdinParams &p) {
  // create a new input file
  // run run_simulator
  // retrieve result
  return result;
}

/// Naive way of optimizing it, model with simple GP prior
struct Param : public SemiParametricModel<Param> {
  Param() {
    p_.default_noise(0.0);

    // replace with plausible range for the prior
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
    output("objective", eng_, p.cycle_time_.value(), p.pipelining_.value());
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
  NLOpt<> opt(p.x1_, p.x2_);

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

  BHParams p;
  BayesOpt<unordered_map<string, double> > opt;

  auto subopt = [&]() {
    maximize_ei(m, p, opt.best_objective());
  };

  auto util = [&](){
    unordered_map<string, double> res;

    //
    res["objective"] = branin_hoo(p);

    PR(p.x1_.value(), p.x2_.value(), res["objective"]);
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
