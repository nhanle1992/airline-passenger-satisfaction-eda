"""Create the approved hypothesis-testing notebook."""

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks/04_hypothesis_testing.ipynb"


def main() -> None:
    cells = [
        new_markdown_cell("""# Airline Passenger Satisfaction — Hypothesis Testing

This notebook implements the approved protocol in `Hypothesis Testing.md`. The outcome is `is_satisfied` (1 = Satisfied; 0 = Neutral or Dissatisfied). All primary tests use α = 0.05, report effect sizes and 95% confidence intervals, and distinguish statistical association from causation."""),
        new_code_cell('''from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from patsy import build_design_matrices
from statsmodels.formula.api import glm
from statsmodels.genmod.families import Binomial
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep
from IPython.display import Markdown, display

warnings.filterwarnings("ignore", category=FutureWarning)
sns.set_theme(style="whitegrid")
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
df = pd.read_csv(ROOT / "data/processed/airline_passenger_satisfaction_cleaned.csv")
ALPHA = 0.05
print(f"Loaded {len(df):,} records.")'''),
        new_code_cell('''def lr_test(full, reduced):
    statistic = 2 * (full.llf - reduced.llf)
    df_diff = int(full.df_model - reduced.df_model)
    return statistic, df_diff, stats.chi2.sf(statistic, df_diff)

def holm_frame(labels, raw_p):
    reject, adjusted, _, _ = multipletests(raw_p, alpha=ALPHA, method="holm")
    return pd.DataFrame({"Comparison": labels, "Raw p-value": raw_p, "Holm p-value": adjusted, "Reject H0": reject})

def odds_ratio_table(model, contains=None):
    ci = model.conf_int()
    out = pd.DataFrame({"Term": model.params.index, "Odds ratio": np.exp(model.params),
                        "CI low": np.exp(ci[0]), "CI high": np.exp(ci[1]), "p-value": model.pvalues})
    if contains:
        out = out[out["Term"].str.contains(contains, regex=True)]
    return out.reset_index(drop=True)

def standardized_probabilities(model, data, variable, values):
    result = []
    for value in values:
        scenario = data.copy()
        scenario[variable] = value
        design = np.asarray(build_design_matrices([model.model.data.design_info], scenario)[0])
        probability = model.family.link.inverse(design @ model.params.to_numpy())
        estimate = probability.mean()
        gradient = (probability * (1-probability))[:,None] * design
        average_gradient = gradient.mean(axis=0)
        variance = average_gradient @ model.cov_params().to_numpy() @ average_gradient
        standard_error = np.sqrt(max(variance, 0))
        result.append({"Level": value, "Predicted probability": estimate,
                       "CI low": max(0, estimate - 1.96*standard_error),
                       "CI high": min(1, estimate + 1.96*standard_error)})
    return pd.DataFrame(result)

def model_diagnostics(model, label):
    fitted = model.fittedvalues
    return {"Model": label, "N": int(model.nobs), "McFadden pseudo-R2": 1-model.llf/model.llnull,
            "Converged": bool(model.converged),
            "Min fitted probability": fitted.min(), "Max fitted probability": fitted.max(),
            "Deviance/df residual": model.deviance/model.df_resid}'''),
        new_markdown_cell("""## 1. Preliminary checks

Departure and arrival delays measure closely related portions of the same journey. Their correlation is checked before adjusted models; highly correlated versions are not included together in primary adjusted models."""),
        new_code_cell('''delay_complete = df.dropna(subset=["arrival_delay"])
delay_corr = delay_complete[["departure_delay", "arrival_delay"]].corr().iloc[0,1]
sample_summary = pd.DataFrame({
    "Quantity": ["Full dataset", "Missing arrival delay", "Departure/arrival delay correlation"],
    "Value": [f"{len(df):,}", f"{df.arrival_delay.isna().sum():,}", f"{delay_corr:.3f}"]
})
display(sample_summary.style.hide(axis="index"))
display(Markdown(f"Departure and arrival delays correlate at **{delay_corr:.3f}**. Therefore, departure delay is used in the main adjusted models for Hypotheses 1 and 2; arrival delay replaces it in sensitivity models."))'''),
        new_markdown_cell("""## 2. Hypothesis 1 — Service quality and satisfaction

**Primary test:** likelihood-ratio comparison of a logistic model containing categorical cleanliness, seat-comfort, and onboard-service ratings against an intercept-only model. Clean fields exclude undocumented zero ratings."""),
        new_code_cell('''h1_vars = ["cleanliness_rating_clean", "seat_comfort_rating_clean", "onboard_service_rating_clean"]
h1 = df.dropna(subset=h1_vars + ["is_satisfied"]).copy()
service_terms = [f"C({v}, Treatment(reference=1))" for v in h1_vars]
h1_formula = "is_satisfied ~ " + " + ".join(service_terms)
h1_full = glm(h1_formula, data=h1, family=Binomial()).fit()
h1_null = glm("is_satisfied ~ 1", data=h1, family=Binomial()).fit()
h1_lr, h1_df, h1_p = lr_test(h1_full, h1_null)
h1_primary = pd.DataFrame({"Analysis N":[len(h1)], "Excluded":[len(df)-len(h1)], "LR statistic":[h1_lr], "df":[h1_df], "p-value":[h1_p], "Decision":["Reject H0" if h1_p < ALPHA else "Fail to reject H0"]})
display(h1_primary.style.format({"Analysis N":"{:,}","Excluded":"{:,}","LR statistic":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))
display(Markdown("**Rating-level odds ratios (reference = rating 1)**"))
display(odds_ratio_table(h1_full, "rating_clean").style.format({"Odds ratio":"{:.2f}","CI low":"{:.2f}","CI high":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))'''),
        new_code_cell('''drop_results=[]
for variable, term in zip(h1_vars, service_terms):
    reduced_terms=[t for t in service_terms if t != term]
    reduced=glm("is_satisfied ~ " + " + ".join(reduced_terms), data=h1, family=Binomial()).fit()
    stat, dfd, p=lr_test(h1_full,reduced)
    drop_results.append((variable,stat,dfd,p))
h1_drop=pd.DataFrame(drop_results,columns=["Service","LR statistic","df","Raw p-value"])
h1_drop["Holm p-value"]=multipletests(h1_drop["Raw p-value"],method="holm")[1]
h1_drop["Reject service-level H0"]=h1_drop["Holm p-value"]<ALPHA
display(h1_drop.style.format({"LR statistic":"{:.2f}","Raw p-value":"{:.3e}","Holm p-value":"{:.3e}"}).hide(axis="index"))

h1_prob=[]
for variable in h1_vars:
    table=standardized_probabilities(h1_full,h1,variable,[1,2,3,4,5])
    table.insert(0,"Service",variable.replace("_rating_clean","").replace("_"," ").title())
    h1_prob.append(table)
h1_prob=pd.concat(h1_prob,ignore_index=True)
display(h1_prob.style.format({"Predicted probability":"{:.1%}","CI low":"{:.1%}","CI high":"{:.1%}"}).hide(axis="index"))
fig,ax=plt.subplots(figsize=(9,5))
sns.lineplot(data=h1_prob,x="Level",y="Predicted probability",hue="Service",marker="o",ax=ax)
ax.set(title="Standardized satisfaction probability by service rating",xlabel="Rating",ylabel="Predicted probability",ylim=(0,1));
ax.yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1)); plt.tight_layout(); plt.show()'''),
        new_code_cell('''adjusters = "age + C(gender) + C(customer_type) + C(travel_type) + C(travel_class) + np.log1p(flight_distance) + np.log1p(departure_delay)"
h1_adj_formula = h1_formula + " + " + adjusters
h1_adj = glm(h1_adj_formula, data=h1, family=Binomial()).fit()
h1_adj_reduced = glm("is_satisfied ~ " + adjusters, data=h1, family=Binomial()).fit()
h1_adj_lr,h1_adj_df,h1_adj_p=lr_test(h1_adj,h1_adj_reduced)
h1_trend=glm("is_satisfied ~ cleanliness_rating_clean + seat_comfort_rating_clean + onboard_service_rating_clean + " + adjusters,data=h1,family=Binomial()).fit()
h1_sensitivity=glm("is_satisfied ~ cleanliness_rating + seat_comfort_rating + onboard_service_rating",data=df,family=Binomial()).fit()
display(pd.DataFrame([{"Model":"Adjusted categorical service model","N":int(h1_adj.nobs),"LR statistic":h1_adj_lr,"df":h1_adj_df,"p-value":h1_adj_p,"Decision":"Reject H0" if h1_adj_p<ALPHA else "Fail to reject H0"}]).style.format({"N":"{:,}","LR statistic":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))
display(Markdown("**Adjusted ordered-trend odds ratios per one-point rating increase**"))
display(odds_ratio_table(h1_trend,"cleanliness_rating_clean|seat_comfort_rating_clean|onboard_service_rating_clean").style.format({"Odds ratio":"{:.2f}","CI low":"{:.2f}","CI high":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))
display(pd.DataFrame([model_diagnostics(h1_full,"Primary unadjusted"),model_diagnostics(h1_adj,"Adjusted")]).style.format({"McFadden pseudo-R2":"{:.3f}","Min fitted probability":"{:.4f}","Max fitted probability":"{:.4f}","Deviance/df residual":"{:.3f}"}).hide(axis="index"))'''),
        new_code_cell('''# Prespecified H1 sensitivity analyses
h1_zero_formula="is_satisfied ~ C(cleanliness_rating) + C(seat_comfort_rating) + C(onboard_service_rating)"
h1_zero=glm(h1_zero_formula,data=df,family=Binomial()).fit(); h1_zero_null=glm("is_satisfied ~ 1",data=df,family=Binomial()).fit()
h1_zero_lr=lr_test(h1_zero,h1_zero_null)
h1_core=glm("is_satisfied ~ core_service_score_clean",data=h1,family=Binomial()).fit(); h1_core_null=glm("is_satisfied ~ 1",data=h1,family=Binomial()).fit(); h1_core_lr=lr_test(h1_core,h1_core_null)
h1_arr_data=h1.dropna(subset=["arrival_delay"]).copy()
h1_arr_adjusters="age + C(gender) + C(customer_type) + C(travel_type) + C(travel_class) + np.log1p(flight_distance) + np.log1p(arrival_delay)"
h1_arr=glm(h1_formula+" + "+h1_arr_adjusters,data=h1_arr_data,family=Binomial()).fit(); h1_arr_reduced=glm("is_satisfied ~ "+h1_arr_adjusters,data=h1_arr_data,family=Binomial()).fit(); h1_arr_lr=lr_test(h1_arr,h1_arr_reduced)
h1_sens=pd.DataFrame([
    {"Sensitivity analysis":"Original zero-inclusive categorical ratings","N":len(df),"LR statistic":h1_zero_lr[0],"df":h1_zero_lr[1],"p-value":h1_zero_lr[2]},
    {"Sensitivity analysis":"Clean core-service score trend","N":len(h1),"LR statistic":h1_core_lr[0],"df":h1_core_lr[1],"p-value":h1_core_lr[2]},
    {"Sensitivity analysis":"Adjusted model using arrival instead of departure delay","N":len(h1_arr_data),"LR statistic":h1_arr_lr[0],"df":h1_arr_lr[1],"p-value":h1_arr_lr[2]},
])
display(Markdown("**H1 sensitivity analyses**")); display(h1_sens.style.format({"N":"{:,}","LR statistic":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))'''),
        new_markdown_cell("""## 3. Hypothesis 2 — Travel class and satisfaction

**Primary test:** Pearson chi-square test of the 3 × 2 travel-class by satisfaction table. Planned Business-versus-Economy and Business-versus-Economy-Plus proportion comparisons receive Holm correction."""),
        new_code_cell('''h2_table=pd.crosstab(df["travel_class"],df["satisfaction"]).reindex(["Business","Economy","Economy Plus"])
chi2,p_h2,dof,expected=stats.chi2_contingency(h2_table)
n=h2_table.to_numpy().sum(); cramers_v=np.sqrt(chi2/(n*min(h2_table.shape[0]-1,h2_table.shape[1]-1)))
display(h2_table.style.format("{:,}"))
display(pd.DataFrame([{"N":n,"Chi-square":chi2,"df":dof,"p-value":p_h2,"Minimum expected count":expected.min(),"Cramer's V":cramers_v,"Decision":"Reject H0" if p_h2<ALPHA else "Fail to reject H0"}]).style.format({"N":"{:,}","Chi-square":"{:.2f}","p-value":"{:.3e}","Minimum expected count":"{:.1f}","Cramer's V":"{:.3f}"}).hide(axis="index"))

rates=df.groupby("travel_class").is_satisfied.agg(["sum","count","mean"]).reindex(["Business","Economy","Economy Plus"])
comparisons=[]
raw=[]
for other in ["Economy","Economy Plus"]:
    count=np.array([rates.loc["Business","sum"],rates.loc[other,"sum"]]); obs=np.array([rates.loc["Business","count"],rates.loc[other,"count"]])
    z,p=proportions_ztest(count,obs,alternative="two-sided")
    low,high=confint_proportions_2indep(count[0],obs[0],count[1],obs[1],compare="diff",method="newcomb")
    comparisons.append({"Comparison":f"Business vs {other}","Business rate":rates.loc["Business","mean"],"Other rate":rates.loc[other,"mean"],"Difference":rates.loc["Business","mean"]-rates.loc[other,"mean"],"CI low":low,"CI high":high,"z":z,"Raw p-value":p}); raw.append(p)
h2_contrasts=pd.DataFrame(comparisons); h2_contrasts["Holm p-value"]=multipletests(raw,method="holm")[1]; h2_contrasts["Reject contrast H0"]=h2_contrasts["Holm p-value"]<ALPHA
display(h2_contrasts.style.format({"Business rate":"{:.1%}","Other rate":"{:.1%}","Difference":"{:.1%}","CI low":"{:.1%}","CI high":"{:.1%}","z":"{:.2f}","Raw p-value":"{:.3e}","Holm p-value":"{:.3e}"}).hide(axis="index"))'''),
        new_code_cell('''h2_formula="is_satisfied ~ C(travel_class, Treatment(reference='Business')) + age + C(gender) + C(customer_type) + C(travel_type) + np.log1p(flight_distance) + np.log1p(departure_delay)"
h2_adj=glm(h2_formula,data=df,family=Binomial()).fit()
h2_reduced=glm("is_satisfied ~ age + C(gender) + C(customer_type) + C(travel_type) + np.log1p(flight_distance) + np.log1p(departure_delay)",data=df,family=Binomial()).fit()
h2_lr,h2_df,h2_p=lr_test(h2_adj,h2_reduced)
h2_probs=standardized_probabilities(h2_adj,df,"travel_class",["Business","Economy Plus","Economy"])
display(pd.DataFrame([{"Adjusted-model N":int(h2_adj.nobs),"Class LR statistic":h2_lr,"df":h2_df,"p-value":h2_p,"Decision":"Reject H0" if h2_p<ALPHA else "Fail to reject H0"}]).style.format({"Adjusted-model N":"{:,}","Class LR statistic":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))
display(Markdown("**Adjusted class odds ratios (reference = Business)**")); display(odds_ratio_table(h2_adj,"travel_class").style.format({"Odds ratio":"{:.2f}","CI low":"{:.2f}","CI high":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))
display(Markdown("**Standardized adjusted satisfaction probabilities**")); display(h2_probs.style.format({"Predicted probability":"{:.1%}","CI low":"{:.1%}","CI high":"{:.1%}"}).hide(axis="index"))
display(pd.DataFrame([model_diagnostics(h2_adj,"Adjusted class model")]).style.format({"McFadden pseudo-R2":"{:.3f}","Min fitted probability":"{:.4f}","Max fitted probability":"{:.4f}","Deviance/df residual":"{:.3f}"}).hide(axis="index"))'''),
        new_code_cell('''# Prespecified H2 sensitivity and subgroup analyses
h2_arr_data=df.dropna(subset=["arrival_delay"]).copy()
h2_arr_formula="is_satisfied ~ C(travel_class, Treatment(reference='Business')) + age + C(gender) + C(customer_type) + C(travel_type) + np.log1p(flight_distance) + np.log1p(arrival_delay)"
h2_arr=glm(h2_arr_formula,data=h2_arr_data,family=Binomial()).fit(); h2_arr_reduced=glm("is_satisfied ~ age + C(gender) + C(customer_type) + C(travel_type) + np.log1p(flight_distance) + np.log1p(arrival_delay)",data=h2_arr_data,family=Binomial()).fit(); h2_arr_lr=lr_test(h2_arr,h2_arr_reduced)
h2_subgroups=[]
for grouping,level in [("travel_type","Business"),("travel_type","Personal"),("customer_type","Returning"),("customer_type","First-time")]:
    subset=df[df[grouping]==level]; tab=pd.crosstab(subset.travel_class,subset.satisfaction); stat,p,dof,_=stats.chi2_contingency(tab)
    h2_subgroups.append({"Stratum":f"{grouping} = {level}","N":len(subset),"Chi-square":stat,"df":dof,"p-value":p})
display(Markdown("**H2 arrival-delay sensitivity**")); display(pd.DataFrame([{"Analysis":"Adjusted class model using arrival instead of departure delay","N":len(h2_arr_data),"LR statistic":h2_arr_lr[0],"df":h2_arr_lr[1],"p-value":h2_arr_lr[2]}]).style.format({"N":"{:,}","LR statistic":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))
display(Markdown("**Prespecified stratified global class comparisons**")); display(pd.DataFrame(h2_subgroups).style.format({"N":"{:,}","Chi-square":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))'''),
        new_markdown_cell("""## 4. Hypothesis 3 — Flight delays and satisfaction

Departure and arrival delay are tested separately. A natural cubic spline with fixed knots at 15, 60, and 180 dataset units is compared with a linear form. The spline is retained if its additional nonlinear terms improve fit at α = 0.05. Holm correction is applied across the two primary delay tests."""),
        new_code_cell('''def delay_models(data, variable):
    linear=glm(f"is_satisfied ~ {variable}",data=data,family=Binomial()).fit()
    spline=glm(f"is_satisfied ~ cr({variable}, knots=(15,60,180), constraints='center')",data=data,family=Binomial()).fit()
    null=glm("is_satisfied ~ 1",data=data,family=Binomial()).fit()
    nonlin=lr_test(spline,linear); global_test=lr_test(spline,null)
    return linear,spline,nonlin,global_test

h3_dep=df.dropna(subset=["departure_delay","is_satisfied"]).copy()
h3_arr=df.dropna(subset=["arrival_delay","is_satisfied"]).copy()
dep_lin,dep_spline,dep_nonlin,dep_global=delay_models(h3_dep,"departure_delay")
arr_lin,arr_spline,arr_nonlin,arr_global=delay_models(h3_arr,"arrival_delay")
h3_shape=pd.DataFrame([
    {"Exposure":"Departure delay","N":len(h3_dep),"Nonlinearity LR":dep_nonlin[0],"df":dep_nonlin[1],"Nonlinearity p":dep_nonlin[2],"Selected form":"Spline" if dep_nonlin[2]<ALPHA else "Linear"},
    {"Exposure":"Arrival delay","N":len(h3_arr),"Nonlinearity LR":arr_nonlin[0],"df":arr_nonlin[1],"Nonlinearity p":arr_nonlin[2],"Selected form":"Spline" if arr_nonlin[2]<ALPHA else "Linear"}
])
display(h3_shape.style.format({"N":"{:,}","Nonlinearity LR":"{:.2f}","Nonlinearity p":"{:.3e}"}).hide(axis="index"))
selected=[dep_spline if dep_nonlin[2]<ALPHA else dep_lin,arr_spline if arr_nonlin[2]<ALPHA else arr_lin]
global_values=[dep_global if dep_nonlin[2]<ALPHA else lr_test(dep_lin,glm("is_satisfied ~ 1",data=h3_dep,family=Binomial()).fit()),arr_global if arr_nonlin[2]<ALPHA else lr_test(arr_lin,glm("is_satisfied ~ 1",data=h3_arr,family=Binomial()).fit())]
h3_primary=pd.DataFrame([{"Exposure":"Departure delay","N":len(h3_dep),"LR statistic":global_values[0][0],"df":global_values[0][1],"Raw p-value":global_values[0][2]}, {"Exposure":"Arrival delay","N":len(h3_arr),"LR statistic":global_values[1][0],"df":global_values[1][1],"Raw p-value":global_values[1][2]}])
h3_primary["Holm p-value"]=multipletests(h3_primary["Raw p-value"],method="holm")[1]; h3_primary["Decision"]=np.where(h3_primary["Holm p-value"]<ALPHA,"Reject H0","Fail to reject H0")
display(h3_primary.style.format({"N":"{:,}","LR statistic":"{:.2f}","Raw p-value":"{:.3e}","Holm p-value":"{:.3e}"}).hide(axis="index"))'''),
        new_code_cell('''delay_values=[0,15,30,60,120]
delay_predictions=[]
for label,data,variable,model in [("Departure",h3_dep,"departure_delay",selected[0]),("Arrival",h3_arr,"arrival_delay",selected[1])]:
    pred=standardized_probabilities(model,data,variable,delay_values); pred.insert(0,"Delay type",label); delay_predictions.append(pred)
delay_predictions=pd.concat(delay_predictions,ignore_index=True)
delay_predictions["Difference vs 0"] = delay_predictions.groupby("Delay type")["Predicted probability"].transform(lambda x:x-x.iloc[0])
display(delay_predictions.style.format({"Predicted probability":"{:.1%}","CI low":"{:.1%}","CI high":"{:.1%}","Difference vs 0":"{:+.1%}"}).hide(axis="index"))
fig,ax=plt.subplots(figsize=(9,5)); sns.lineplot(data=delay_predictions,x="Level",y="Predicted probability",hue="Delay type",marker="o",ax=ax)
ax.set(title="Model-based satisfaction probability across delay values",xlabel="Delay (dataset units)",ylabel="Predicted probability"); ax.yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1)); plt.tight_layout(); plt.show()'''),
        new_code_cell('''adjustment="age + C(gender) + C(customer_type) + C(travel_type) + C(travel_class) + np.log1p(flight_distance)"
adjusted_results=[]; adjusted_models={}
for label,data,variable,use_spline in [("Departure delay",h3_dep,"departure_delay",dep_nonlin[2]<ALPHA),("Arrival delay",h3_arr,"arrival_delay",arr_nonlin[2]<ALPHA)]:
    term=f"cr({variable}, knots=(15,60,180), constraints='center')" if use_spline else variable
    full=glm(f"is_satisfied ~ {term} + {adjustment}",data=data,family=Binomial()).fit()
    reduced=glm(f"is_satisfied ~ {adjustment}",data=data,family=Binomial()).fit()
    stat,dfd,p=lr_test(full,reduced); adjusted_models[label]=full
    adjusted_results.append({"Exposure":label,"N":int(full.nobs),"LR statistic":stat,"df":dfd,"Raw p-value":p})
h3_adjusted=pd.DataFrame(adjusted_results); h3_adjusted["Holm p-value"]=multipletests(h3_adjusted["Raw p-value"],method="holm")[1]; h3_adjusted["Decision"]=np.where(h3_adjusted["Holm p-value"]<ALPHA,"Reject H0","Fail to reject H0")
display(h3_adjusted.style.format({"N":"{:,}","LR statistic":"{:.2f}","Raw p-value":"{:.3e}","Holm p-value":"{:.3e}"}).hide(axis="index"))

adj_predictions=[]
for label,data,variable in [("Departure delay",h3_dep,"departure_delay"),("Arrival delay",h3_arr,"arrival_delay")]:
    pred=standardized_probabilities(adjusted_models[label],data,variable,delay_values); pred.insert(0,"Exposure",label); adj_predictions.append(pred)
adj_predictions=pd.concat(adj_predictions,ignore_index=True); adj_predictions["Difference vs 0"]=adj_predictions.groupby("Exposure")["Predicted probability"].transform(lambda x:x-x.iloc[0])
display(adj_predictions.style.format({"Predicted probability":"{:.1%}","CI low":"{:.1%}","CI high":"{:.1%}","Difference vs 0":"{:+.1%}"}).hide(axis="index"))
display(pd.DataFrame([model_diagnostics(adjusted_models[k],f"Adjusted {k}") for k in adjusted_models]).style.format({"McFadden pseudo-R2":"{:.3f}","Min fitted probability":"{:.4f}","Max fitted probability":"{:.4f}","Deviance/df residual":"{:.3f}"}).hide(axis="index"))'''),
        new_code_cell('''band_results=[]
for variable,reference in [("departure_delay_band","No delay"),("arrival_delay_band","No delay")]:
    data=df if variable=="departure_delay_band" else df[df[variable]!="Missing"]
    model=glm(f"is_satisfied ~ C({variable}, Treatment(reference='{reference}'))",data=data,family=Binomial()).fit()
    table=odds_ratio_table(model,variable); table.insert(0,"Exposure",variable); band_results.append(table)
display(pd.concat(band_results,ignore_index=True).style.format({"Odds ratio":"{:.2f}","CI low":"{:.2f}","CI high":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))'''),
        new_code_cell('''# Prespecified H3 sensitivity analyses
h3_sensitivity=[]
for label,data,variable in [("Departure",h3_dep,"departure_delay"),("Arrival",h3_arr,"arrival_delay")]:
    null=glm("is_satisfied ~ 1",data=data,family=Binomial()).fit()
    log_model=glm(f"is_satisfied ~ np.log1p({variable})",data=data,family=Binomial()).fit(); log_lr=lr_test(log_model,null)
    cap=data[variable].quantile(.99); capped=data.copy(); capped[f"{variable}_winsor99"]=capped[variable].clip(upper=cap)
    cap_model=glm(f"is_satisfied ~ {variable}_winsor99",data=capped,family=Binomial()).fit(); cap_null=glm("is_satisfied ~ 1",data=capped,family=Binomial()).fit(); cap_lr=lr_test(cap_model,cap_null)
    h3_sensitivity.extend([
        {"Exposure":label,"Sensitivity":"log1p transformation","N":len(data),"LR statistic":log_lr[0],"df":log_lr[1],"p-value":log_lr[2]},
        {"Exposure":label,"Sensitivity":f"99th-percentile winsorized (cap={cap:.0f})","N":len(data),"LR statistic":cap_lr[0],"df":cap_lr[1],"p-value":cap_lr[2]},
    ])
arrival_missing_model=glm("is_satisfied ~ C(arrival_delay_band, Treatment(reference='No delay'))",data=df,family=Binomial()).fit()
arrival_missing_or=odds_ratio_table(arrival_missing_model,"Missing")
display(pd.DataFrame(h3_sensitivity).style.format({"N":"{:,}","LR statistic":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))
display(Markdown("**Arrival-delay Missing category versus No delay**")); display(arrival_missing_or.style.format({"Odds ratio":"{:.2f}","CI low":"{:.2f}","CI high":"{:.2f}","p-value":"{:.3e}"}).hide(axis="index"))'''),
        new_markdown_cell("""## 5. Decision summary and interpretation"""),
        new_code_cell('''summary=pd.DataFrame([
    {"Hypothesis":"H1: Service quality","Primary p-value":h1_p,"Decision":"Reject H0" if h1_p<ALPHA else "Fail to reject H0"},
    {"Hypothesis":"H2: Travel class","Primary p-value":p_h2,"Decision":"Reject H0" if p_h2<ALPHA else "Fail to reject H0"},
    {"Hypothesis":"H3a: Departure delay","Primary p-value":h3_primary.loc[0,"Holm p-value"],"Decision":h3_primary.loc[0,"Decision"]},
    {"Hypothesis":"H3b: Arrival delay","Primary p-value":h3_primary.loc[1,"Holm p-value"],"Decision":h3_primary.loc[1,"Decision"]},
])
display(summary.style.format({"Primary p-value":"{:.3e}"}).hide(axis="index"))
display(Markdown("""
- Rejecting a null hypothesis indicates evidence of an association in this dataset; it does not demonstrate causation.
- Effect sizes and predicted-probability differences should guide business interpretation because the large sample can make small effects statistically significant.
- Adjusted models address observed covariates only. Unmeasured factors such as route, fare, aircraft, loyalty tier, and disruption cause can still confound results.
- `Neutral or Dissatisfied` is a combined outcome and cannot distinguish neutral from actively dissatisfied passengers.
"""))'''),
    ]
    nb = new_notebook(cells=cells, metadata={"kernelspec":{"display_name":"Python (Airlines Satisfaction)","language":"python","name":"airlines-satisfaction"},"language_info":{"name":"python","version":"3.13"}})
    nbformat.write(nb, OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
