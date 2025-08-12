library(dplyr)
library(tidyr)
library(ggplot2)
library(purrr)
library(scales)
library(readxl)
library(readr)
library(Hmisc)
library(tibble)

## Helper
pad5 <- function(x) { x <- as.character(x); n <- nchar(x); need <- pmax(0, 5 - n); paste0(strrep("0", need), x) }

# Standardize a metric (e.g., LE) to national subgroup composition
# df: long data (one row per unit × subgroup)
# unit_cols: character vector of unit IDs (e.g., "cz" or c("state","cz"))
# subgroup_cols: character vector of subgroup IDs (e.g., "race" or c("race","inc_q"))
# value_col: column name of subgroup-specific metric (e.g., "LE40")
# n_col: column name of the subgroup count (e.g., "n")
# out_col: name for adjusted value per unit
# renorm_within_unit: if TRUE, re-normalize national weights within each unit
#   over the subgroups that are observed (recommended)
standardize_by_national <- function(df, unit_cols, subgroup_cols, value_col, n_col,
                                    out_col = "LE_adj", renorm_within_unit = TRUE) {
  stopifnot(all(unit_cols %in% names(df)),
            all(subgroup_cols %in% names(df)),
            value_col %in% names(df),
            n_col %in% names(df))
  
  # 1) National weights from n (joint over subgroup_cols)
  nat_w <- df |>
    dplyr::group_by(dplyr::across(dplyr::all_of(subgroup_cols))) |>
    dplyr::summarise(n_nat = sum(.data[[n_col]], na.rm = TRUE), .groups = "drop") |>
    dplyr::mutate(w_nat = n_nat / sum(n_nat, na.rm = TRUE))
  
  # 2) Attach national weights
  df_w <- df |>
    dplyr::left_join(nat_w, by = subgroup_cols)
  
  # 3) For each unit, compute weighted average using national weights
  out <- df_w |>
    dplyr::group_by(dplyr::across(dplyr::all_of(unit_cols))) |>
    dplyr::summarise(
      !!out_col := {
        ok <- is.finite(.data[[value_col]]) & is.finite(.data[["w_nat"]]) & (.data[["w_nat"]] > 0)
        if (!any(ok)) {
          NA_real_
        } else {
          w <- .data[["w_nat"]][ok]
          v <- .data[[value_col]][ok]
          if (renorm_within_unit) w <- w / sum(w)  # renormalize over observed subgroups
          sum(w * v, na.rm = TRUE)
        }
      },
      .groups = "drop"
    )
  
  out
}


## =========================
## Example Usage
## =========================

#Race-adjusted LE per CZ
#standardize_by_national(df, unit_cols = "cz", subgroup_cols = "race", value_col = "LE40", n_col = "n")

#racexincome-adjusted LE per CZ
#standardize_by_national(df, unit_cols = "cz", subgroup_cols = c("race","inc_q"), value_col = "LE40", n_col = "n")

## =========================
## Weighted correlation util
## =========================
# Computes a Pearson correlation weighted by counts (e.g., population),
# plus an approximate SE using Fisher z with effective sample size.
# - x, y: numeric vectors
# - w:    OPTIONAL raw weights (e.g., total_pop). If NULL → unweighted.
# Behavior:
# - Uses pairwise-complete on x,y so your dataset is never modified.
# - Treats non-finite weights (NA/Inf) as zero; drops non-positive weights.
# - Normalizes weights to sum to 1 (probability weights).
# - Effective n: n_eff = 1 / sum(w^2) with normalized weights.
cor_with_se_w <- function(x, y, w = NULL) {
  # 1) Pairwise completeness on x,y only (do not alter the data frame)
  ok_xy <- complete.cases(x, y)
  x <- x[ok_xy]
  y <- y[ok_xy]
  
  # 2) Build weights
  if (is.null(w)) {
    # Unweighted: equal weight to each kept row
    w <- rep(1, length(x))
  } else {
    # Align to the same kept rows; bad weights → 0 so they don't contribute
    w <- w[ok_xy]
    w[!is.finite(w)] <- 0
  }
  
  # 3) Keep strictly positive weights only
  keep <- w > 0
  x <- x[keep]; y <- y[keep]; w <- w[keep]
  
  # If too few observations remain, return NAs
  if (length(w) < 2L) {
    return(c(correlation = NA_real_, se = NA_real_, n_eff = NA_real_))
  }
  
  # 4) Normalize to shares (scale-free, numerically stable)
  s <- sum(w)
  if (s <= 0) {
    return(c(correlation = NA_real_, se = NA_real_, n_eff = NA_real_))
  }
  w <- w / s
  
  # 5) Weighted moments
  mx <- sum(w * x); my <- sum(w * y)
  vx <- sum(w * (x - mx)^2)
  vy <- sum(w * (y - my)^2)
  cov_xy <- sum(w * (x - mx) * (y - my))
  
  # 6) Weighted Pearson r
  r <- if (vx > 0 && vy > 0) cov_xy / sqrt(vx * vy) else NA_real_
  
  # 7) Effective sample size and SE via Fisher z
  n_eff <- 1 / sum(w^2)  # equals n when weights are equal
  se <- if (!is.na(r) && is.finite(r) && n_eff > 3) (1 - r^2) / sqrt(n_eff - 3) else NA_real_
  
  c(correlation = r, se = se, n_eff = n_eff)
}


## Data
cty_characteristics <- read.csv("cty_characteristics.csv") %>%
  mutate(FIPS = pad5(FIPS))

mortality <- read.csv("cty_mortality.csv") %>%
  filter(year != 2001) %>%
  mutate(FIPS = pad5(county)) %>%
  select(-county)

mortality_merged <- mortality %>%
  left_join(cty_characteristics, by = "FIPS")

## Predictors
vars_to_cor <- c(
  "fei","pc_physicians_pc","mh_centers_pc",
  "CSMOKING_AdjPrev","OBESITY_AdjPrev",
  "cur_smoke_q1","cur_smoke_q2","cur_smoke_q3","cur_smoke_q4",
  "bmi_obese_q1","bmi_obese_q2","bmi_obese_q3","bmi_obese_q4",
  "exercise_any_q1","exercise_any_q2","exercise_any_q3","exercise_any_q4",
  "LPA_AdjPrev","BINGE_AdjPrev",
  "puninsured2010","reimb_penroll_adj10","mort_30day_hosp_z","med_prev_qual_z",
  "total_opiate_pc","CODEINE_pc","FENTANYL_pc","HYDROCODONE_pc","HYDROMORPHONE_pc",
  "MEPERIDINE_pc","MORPHINE_pc","OXYCODONE_pc",
  "cs00_seg_inc","PM","water","pct_pre1960",
  "gini99","scap_ski90pcm","inc_share_1perc","frac_middleclass",
  "kfr_pooled_pooled_p25_1992","change_kfr_pooled_pooled_p25",
  "cs_labforce","unemp_2019","unemp_diff_2001_2019","pct_change_lf",
  "poor_share","crime_total","rel_tot",
  "cs_fam_wkidsinglemom","cs_born_foreign","pop_density",
  "subcty_exp_pc","taxrate","tax_st_diff_top20",
  "median_house_value","hhinc00","pct_change_pop","pct_black",
  "score_r","cs_educ_ba","dropout_r","ccd_exp_tot"
)

## Causes
causes_keep <- c("All",
                 "External causes, overdose",
                 "External causes, suicide",
                 "Digestive diseases, alcohol liver disease")

## --- weighted correlations by education (weights = total_pop) ---
corr_by_edu_w <- mortality_merged %>%
  filter(cause %in% causes_keep) %>%
  group_by(cause, education) %>%
  group_modify(~ {
    map_dfr(vars_to_cor, function(v) {
      out <- cor_with_se_w(.x[[v]], .x$mr_adjusted, .x$total_pop)
      tibble(variable = v,
             correlation = unname(out["correlation"]),
             se          = unname(out["se"]),
             n_eff       = unname(out["n_eff"]))
    })
  }) %>%
  ungroup() %>%
  mutate(grouping = "By education (pop-weighted)")

## --- weighted correlations without education split ---
corr_all_edu_w <- mortality_merged %>%
  filter(cause %in% causes_keep) %>%
  group_by(cause) %>%
  group_modify(~ {
    map_dfr(vars_to_cor, function(v) {
      out <- cor_with_se_w(.x[[v]], .x$mr_adjusted, .x$total_pop)
      tibble(variable = v,
             correlation = unname(out["correlation"]),
             se          = unname(out["se"]),
             n_eff       = unname(out["n_eff"]))
    })
  }) %>%
  ungroup() %>%
  mutate(education = "All", grouping = "No education split (pop-weighted)")

## Combine
corr_combined <- bind_rows(corr_by_edu_w, corr_all_edu_w)



## --- 1. Rename lookup -------------------------------------------
  var_rename <- c(
    CSMOKING_AdjPrev = "% Current smokers (2019)",
    OBESITY_AdjPrev = "Obesity rate 2019",
    cur_smoke_q1 = "Smokers Q1 (96-08)",
    cur_smoke_q2 = "Smokers Q2 (96-08)",
    cur_smoke_q3 = "Smokers Q3 (96-08)",
    cur_smoke_q4 = "Smokers Q4 (96-08)",
    bmi_obese_q1 = "Obese Q1 (96-08)",
    bmi_obese_q2 = "Obese Q2 (96-08)",
    bmi_obese_q3 = "Obese Q3 (96-08)",
    bmi_obese_q4 = "Obese Q4 (96-08)",
    exercise_any_q1 = "Exercise Q1 (96-08)",
    exercise_any_q2 = "Exercise Q2 (96-08)",
    exercise_any_q3 = "Exercise Q3 (96-08)",
    exercise_any_q4 = "Exercise Q4 (96-08)",
    LPA_AdjPrev = "% Physically inactive (2019)",
    BINGE_AdjPrev = "% Binge drinkers (2019)",
    fei = "Food environment index",
    pc_physicians_pc = "Primary care physicians (per capita)",
    mh_centers_pc = "Mental health centers (per capita)",
    puninsured2010 = "% Uninsured",
    reimb_penroll_adj10 = "Medicare $ per enrollee",
    mort_30day_hosp_z = "30-day hospital mortality index",
    med_prev_qual_z = "Preventive care index",
    total_opiate_pc = "Opiate shipments pc",
    CODEINE_pc = "Codeine pc",
    FENTANYL_pc = "Fentanyl pc",
    HYDROCODONE_pc = "Hydrocodone pc",
    HYDROMORPHONE_pc = "Hydromorphone pc",
    MEPERIDINE_pc = "Meperidine pc",
    MORPHINE_pc = "Morphine pc",
    OXYCODONE_pc = "Oxycodone pc",
    cs00_seg_inc = "Income segregation",
    PM = "PM2.5 concentration",
    water = "Drinking water violations",
    pct_pre1960 = "Lead exposure",
    gini99 = "Gini index",
    scap_ski90pcm = "Social capital index",
    inc_share_1perc = "Top 1% income share",
    frac_middleclass = "Fraction middle class",
    cs_labforce = "Labor force participation",
    unemp_2019 = "Unemployment rate (%)",
    unemp_diff_2001_2019 = "% Δ unemployment (01–19)",
    pct_change_lf = "% Δ labor force (01–19)",
    poor_share = "Poverty rate",
    crime_total = "Crime rate",
    rel_tot = "% Religious",
    cs_fam_wkidsinglemom = "% Kids w/ single mom",
    cs_born_foreign = "% Immigrants",
    pop_density = "Population density",
    subcty_exp_pc = "Local gov expenditures",
    taxrate = "Tax rate",
    tax_st_diff_top20 = "Tax progressivity",
    median_house_value = "Median house value",
    hhinc00 = "Mean income",
    pct_change_pop = "% Δ population (01–19)",
    pct_black = "% Black",
    score_r = "Test score percentile",
    cs_educ_ba = "% College graduates",
    dropout_r = "HS dropout rate",
    ccd_exp_tot = "School expenditure per student",
    kfr_pooled_pooled_p25_1992 = "Absolute Mobility (1992)",
    change_kfr_pooled_pooled_p25 = "Change in Mobility (78-92)"
  )

## --- 2. Domain (broad group) mapping ------------------------------------
domain_map <- list(
  "Health Behaviors" = c(
    "CSMOKING_AdjPrev","OBESITY_AdjPrev",
    "cur_smoke_q1","cur_smoke_q2","cur_smoke_q3","cur_smoke_q4",
    "bmi_obese_q1","bmi_obese_q2","bmi_obese_q3","bmi_obese_q4",
    "exercise_any_q1","exercise_any_q2","exercise_any_q3","exercise_any_q4",
    "LPA_AdjPrev","BINGE_AdjPrev","fei"
  ),
  "Health Care" = c(
    "pc_physicians_pc","mh_centers_pc","puninsured2010","reimb_penroll_adj10",
    "mort_30day_hosp_z","med_prev_qual_z",
    "total_opiate_pc","CODEINE_pc","FENTANYL_pc","HYDROCODONE_pc",
    "HYDROMORPHONE_pc","MEPERIDINE_pc","MORPHINE_pc","OXYCODONE_pc"
  ),
  "Environmental factors" = c("cs00_seg_inc","PM","water","pct_pre1960"),
  "Social and Economic Conditions" = c(
    "gini99","scap_ski90pcm","inc_share_1perc","frac_middleclass",
    "kfr_pooled_pooled_p25_1992","change_kfr_pooled_pooled_p25",
    "cs_labforce","unemp_2019","unemp_diff_2001_2019",
    "pct_change_lf","poor_share","crime_total","rel_tot"
  ),
  "Population & Socioeconomic Composition" = c(
    "cs_fam_wkidsinglemom","cs_born_foreign","pop_density",
    "subcty_exp_pc","taxrate","tax_st_diff_top20",
    "median_house_value","hhinc00","pct_change_pop","pct_black"
  ),
  "Human capital / Educational quality" = c("score_r","cs_educ_ba","dropout_r","ccd_exp_tot")
)

domain_df <- purrr::imap_dfr(domain_map, ~ tibble(variable = .x, domain = .y))



## --- 3. Cause labels -----------------------------------------------------
cause_labels <- c(
  "All" = "All-Cause",
  "External causes, overdose" = "Overdose",
  "External causes, suicide" = "Suicide",
  "Digestive diseases, alcohol liver disease" = "Alcohol Liver Disease"
)
causes_to_plot <- names(cause_labels)

## --- 4. Function to build one heatmap -----------------------------------
plot_full_heatmap <- function(cause_name) {
  
  df_cause <- corr_combined %>%
    filter(cause == cause_name) %>%
    left_join(domain_df, by = "variable") %>%                 # attach domain
    mutate(variable_label = recode(variable, !!!var_rename))  # nice labels
  
  # order variables within each domain by correlation in "All" education (desc)
  ord_tbl <- df_cause %>%
    filter(education == "All") %>%
    group_by(domain) %>%
    arrange(desc(correlation), .by_group = TRUE) %>%
    mutate(order_in_dom = row_number()) %>%
    ungroup() %>%
    select(variable_label, domain, order_in_dom)
  
  df_cause <- df_cause %>%
    left_join(ord_tbl, by = c("variable_label","domain")) %>%
    arrange(domain, order_in_dom) %>%
    mutate(variable_label = factor(variable_label, levels = unique(variable_label)),
           education = factor(education, levels = c("All","H.S. or less","Some college or more")))
  
  ggplot(df_cause, aes(x = education, y = variable_label, fill = correlation)) +
    geom_tile(color = "white") +
    geom_text(aes(label = round(correlation, 2)), size = 2.7) +
    scale_fill_gradient2(low = "red", mid = "white", high = "blue",
                         midpoint = 0, limits = c(-0.8, 0.8), name = "Correlation") +
    facet_grid(domain ~ ., scales = "free_y", space = "free_y", switch = "y") +
    labs(
      title = paste0("Correlation Coefficients for ", cause_labels[[cause_name]], " Mortality"),
      x = "Education group", y = NULL
    ) +
    theme_minimal(base_size = 12) +
    theme(
      strip.placement = "outside",
      strip.text.y.left = element_text(angle = 0, hjust = 1, face = "bold"),
      axis.text.x = element_text(angle = 30, hjust = 1),
      panel.spacing.y = unit(2, "mm")
    )
}

## --- 5. Loop, print & save ----------------------------------------------
plots <- purrr::imap(causes_to_plot, ~{
  p <- plot_full_heatmap(.x)
  ggsave(paste0("heatmap_full_", gsub("[^A-Za-z0-9]+","_", cause_labels[.x]), ".png"),
         p, width = 9.5, height = 20, dpi = 300)
  p
})

# To view one:
plots[[1]]
