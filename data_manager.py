"""
数据管理模块 - 适配Android
复用桌面版所有计算逻辑，仅修改文件存储路径
"""
import json
import os


def get_data_dir():
    """获取数据存储目录（Android兼容）"""
    try:
        from kivy.utils import platform as kivy_platform
        if kivy_platform == 'android':
            # Android应用私有目录
            from android.storage import app_storage_path
            return app_storage_path()
    except (ImportError, Exception):
        pass
    # 桌面环境：脚本所在目录
    return os.path.dirname(os.path.abspath(__file__))


class DataManager:
    def __init__(self):
        self.data_dir = get_data_dir()
        self.data_file = os.path.join(self.data_dir, "cost_data.json")
        self.analysis_file = os.path.join(self.data_dir, "analysis_data.json")
        
        self.default_data = {
            "raw_materials": [],
            "production_efficiency": {
                "产量_10小时_斤": 0, "产量_小时_斤": 0,
                "产量_每小时_kg": 0, "产量_每小时_吨": 0,
                "工作时间": 8, "天数": 22, "source": "manual"
            },
            "capacity": {"月产能_kg": 0, "月产能_吨": 0},
            "fixed_costs": [],
            "admin_costs": [],
            "electricity": {"电费单价元_kg": 0.5},
            "porter_wages": [],
            "production_wages": [],
            "packaging_wages": [],
            "packaging_coefficient": {
                "上月包装工资": 0, "上月总产量kg": 0, "包装系数": 0
            },
            "product_costs": {"包装膜费用": 0, "纸箱费用": 0},
            "products": [],
            "efficiency_tracking": []
        }
        self.data = {}
        self.load()

    def save(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    for key in self.default_data:
                        if key not in saved:
                            saved[key] = self.default_data[key]
                    self.data = saved
            except Exception:
                self.data = dict(self.default_data)
        else:
            self.data = dict(self.default_data)
            self.save()

    # ==================== 原材料库 ====================
    def add_material(self, name, price_kg):
        self.data["raw_materials"].append({
            "name": name, "price_kg": price_kg, "price_ton": price_kg * 1000
        })
        self.save()

    def delete_material(self, idx):
        if 0 <= idx < len(self.data["raw_materials"]):
            del self.data["raw_materials"][idx]
            self.save()

    def update_material(self, idx, name, price_kg):
        if 0 <= idx < len(self.data["raw_materials"]):
            self.data["raw_materials"][idx] = {
                "name": name, "price_kg": price_kg,
                "price_ton": price_kg * 1000
            }
            self.save()

    def get_material_names(self):
        return [m["name"] for m in self.data["raw_materials"]]

    def get_material_price(self, name):
        for m in self.data["raw_materials"]:
            if m["name"] == name:
                return m["price_kg"]
        return 0

    # ==================== 产品配方 ====================
    def add_product(self, name):
        self.data["products"].append({
            "name": name, "ingredients": [], "input_kg": 0, "output_kg": 0
        })
        self.save()

    def update_product_name(self, idx, name):
        if 0 <= idx < len(self.data["products"]):
            self.data["products"][idx]["name"] = name
            self.save()

    def update_product_ratio(self, idx, input_kg, output_kg):
        if 0 <= idx < len(self.data["products"]):
            self.data["products"][idx]["input_kg"] = input_kg
            self.data["products"][idx]["output_kg"] = output_kg
            self.save()

    def delete_product(self, idx):
        if 0 <= idx < len(self.data["products"]):
            del self.data["products"][idx]
            self.save()

    def add_ingredient(self, product_idx, material_name, usage_kg):
        if 0 <= product_idx < len(self.data["products"]):
            self.data["products"][product_idx]["ingredients"].append({
                "material_name": material_name, "usage_kg": usage_kg
            })
            self.save()

    def update_ingredient(self, product_idx, ing_idx, material_name, usage_kg):
        if 0 <= product_idx < len(self.data["products"]):
            p = self.data["products"][product_idx]
            if 0 <= ing_idx < len(p["ingredients"]):
                p["ingredients"][ing_idx] = {
                    "material_name": material_name, "usage_kg": usage_kg
                }
                self.save()

    def delete_ingredient(self, product_idx, ing_idx):
        if 0 <= product_idx < len(self.data["products"]):
            p = self.data["products"][product_idx]
            if 0 <= ing_idx < len(p["ingredients"]):
                del p["ingredients"][ing_idx]
                self.save()

    def calc_product_raw_cost(self, product_idx):
        """计算产品的原材料总成本"""
        if 0 <= product_idx < len(self.data["products"]):
            product = self.data["products"][product_idx]
            total = 0
            for ing in product["ingredients"]:
                total += ing["usage_kg"] * self.get_material_price(ing["material_name"])
            return total
        return 0

    # ==================== 固定费用 ====================
    def add_fixed_cost(self, name, price):
        self.data["fixed_costs"].append({"name": name, "price": price})
        self.save()

    def update_fixed_cost(self, idx, name, price):
        if 0 <= idx < len(self.data["fixed_costs"]):
            self.data["fixed_costs"][idx] = {"name": name, "price": price}
            self.save()

    def delete_fixed_cost(self, idx):
        if 0 <= idx < len(self.data["fixed_costs"]):
            del self.data["fixed_costs"][idx]
            self.save()

    def total_fixed_costs(self):
        return sum(x["price"] for x in self.data["fixed_costs"])

    # ==================== 管理员费用 ====================
    def add_admin_cost(self, name, price, qty):
        self.data["admin_costs"].append({
            "name": name, "price": price, "qty": qty,
            "total": price * qty
        })
        self.save()

    def update_admin_cost(self, idx, name, price, qty):
        if 0 <= idx < len(self.data["admin_costs"]):
            self.data["admin_costs"][idx] = {
                "name": name, "price": price, "qty": qty,
                "total": price * qty
            }
            self.save()

    def delete_admin_cost(self, idx):
        if 0 <= idx < len(self.data["admin_costs"]):
            del self.data["admin_costs"][idx]
            self.save()

    def total_admin_costs(self):
        return sum(x["total"] for x in self.data["admin_costs"])

    # ==================== 电费 ====================
    def update_electricity_price(self, price_per_kg):
        self.data["electricity"]["电费单价元_kg"] = price_per_kg
        self.save()

    def calc_electricity(self):
        return self.data["capacity"]["月产能_kg"] * self.data["electricity"]["电费单价元_kg"]

    # ==================== 产能 ====================
    def update_capacity(self, field, value):
        cap = self.data["capacity"]
        if field == "kg":
            cap["月产能_kg"] = value
            cap["月产能_吨"] = value / 1000
        elif field == "ton":
            cap["月产能_吨"] = value
            cap["月产能_kg"] = value * 1000
        self.save()

    # ==================== 搬运工工资 ====================
    def add_porter(self, name, wage):
        self.data["porter_wages"].append({
            "name": name, "base_wage": wage,
            "correction": 0, "actual": wage
        })
        self.calc_porter_wages()

    def update_porter(self, idx, name, wage):
        if 0 <= idx < len(self.data["porter_wages"]):
            self.data["porter_wages"][idx]["name"] = name
            self.data["porter_wages"][idx]["base_wage"] = wage
            self.calc_porter_wages()

    def delete_porter(self, idx):
        if 0 <= idx < len(self.data["porter_wages"]):
            del self.data["porter_wages"][idx]
            self.calc_porter_wages()

    def calc_porter_wages(self):
        cap_kg = self.data["capacity"]["月产能_kg"]
        total = len(self.data["porter_wages"])
        if total == 0:
            self.save()
            return
        for p in self.data["porter_wages"]:
            p["correction"] = (cap_kg - 140686) * 0.013765 / total
            p["actual"] = p["base_wage"] + p["correction"]
        self.save()

    def total_porter_wages(self):
        return sum(x["actual"] for x in self.data["porter_wages"])

    # ==================== 生产线员工工资 ====================
    def add_production_worker(self, name, wage, extra_rate, bonus):
        self.data["production_wages"].append({
            "name": name, "base_wage": wage,
            "extra_rate": extra_rate, "bonus": bonus,
            "limit_hours": 0, "actual_hours": 0,
            "diff": 0, "extra_wage": 0, "total": wage + bonus
        })
        self.calc_production_wages()

    def update_production_worker(self, idx, name, wage, extra_rate, bonus):
        if 0 <= idx < len(self.data["production_wages"]):
            w = self.data["production_wages"][idx]
            w["name"] = name
            w["base_wage"] = wage
            w["extra_rate"] = extra_rate
            w["bonus"] = bonus
            self.calc_production_wages()

    def delete_production_worker(self, idx):
        if 0 <= idx < len(self.data["production_wages"]):
            del self.data["production_wages"][idx]
            self.calc_production_wages()

    def calc_production_wages(self):
        cap_kg = self.data["capacity"]["月产能_kg"]
        eff_kg = self.data["production_efficiency"]["产量_每小时_kg"]
        if eff_kg == 0:
            self.save()
            return
        for w in self.data["production_wages"]:
            base = w.get("base_wage", 0)
            rate = w.get("extra_rate", 0)
            bonus = w.get("bonus", 0)
            w["limit_hours"] = base / rate if rate > 0 else 0
            w["actual_hours"] = cap_kg / eff_kg
            w["diff"] = w["actual_hours"] - w["limit_hours"]
            w["extra_wage"] = max(0, w["diff"]) * rate
            if w["actual_hours"] > w["limit_hours"]:
                w["total"] = base + w["extra_wage"] + bonus
            else:
                w["total"] = base + bonus
        self.save()

    def total_production_wages(self):
        return sum(x["total"] for x in self.data["production_wages"])

    # ==================== 包装人员工资 ====================
    def add_packaging_worker(self, name, wage, subsidy, bonus):
        self.data["packaging_wages"].append({
            "name": name, "base_wage": wage, "subsidy": subsidy,
            "bonus": bonus, "total": wage + subsidy + bonus,
            "calibration": 0, "final": 0
        })
        self.calc_packaging_wages()

    def update_packaging_worker(self, idx, name, wage, subsidy, bonus):
        if 0 <= idx < len(self.data["packaging_wages"]):
            w = self.data["packaging_wages"][idx]
            w["name"] = name
            w["base_wage"] = wage
            w["subsidy"] = subsidy
            w["bonus"] = bonus
            w["total"] = wage + subsidy + bonus
            self.calc_packaging_wages()

    def delete_packaging_worker(self, idx):
        if 0 <= idx < len(self.data["packaging_wages"]):
            del self.data["packaging_wages"][idx]
            self.calc_packaging_wages()

    def calc_packaging_wages(self):
        cap_kg = self.data["capacity"]["月产能_kg"]
        coeff = 0
        pc = self.data.get("packaging_coefficient", {})
        if isinstance(pc, dict) and len(pc) > 0:
            values = list(pc.values())
            coeff = values[2] if len(values) >= 3 else values[-1]
        total = len(self.data["packaging_wages"])
        if total == 0:
            self.save()
            return
        for w in self.data["packaging_wages"]:
            w["calibration"] = cap_kg * coeff / total
            base_total = w["base_wage"] + w["subsidy"] + w["bonus"]
            w["final"] = max(w["calibration"], base_total)
        self.save()

    def total_packaging_wages(self):
        return sum(x["final"] for x in self.data["packaging_wages"])

    # ==================== 包装系数 ====================
    def update_packaging_coeff(self, last_wage, last_output):
        pc = self.data["packaging_coefficient"]
        if isinstance(pc, dict):
            keys = list(pc.keys())
            if len(keys) >= 3:
                pc[keys[0]] = last_wage
                pc[keys[1]] = last_output
                pc[keys[2]] = last_wage / last_output if last_output > 0 else 0
            else:
                pc["上月包装工资"] = last_wage
                pc["上月总产量kg"] = last_output
                pc["包装系数"] = last_wage / last_output if last_output > 0 else 0
        self.save()

    # ==================== 产品成本 ====================
    def update_product_costs(self, film, carton):
        self.data["product_costs"]["包装膜费用"] = film
        self.data["product_costs"]["纸箱费用"] = carton
        self.save()

    # ==================== 生产效率 ====================
    def update_pe_manual(self, kg_per_hour):
        self.data["production_efficiency"]["产量_每小时_kg"] = kg_per_hour
        self.data["production_efficiency"]["source"] = "manual"
        self.save()

    def update_pe_source(self, source):
        self.data["production_efficiency"]["source"] = source
        self.save()

    def update_work_time(self, hours, days):
        pe = self.data["production_efficiency"]
        pe["工作时间"] = hours
        pe["天数"] = days
        self.save()

    def get_monthly_capacity(self):
        pe = self.data["production_efficiency"]
        return pe["产量_每小时_kg"] * pe["工作时间"] * pe["天数"]

    # ==================== 参考项目（B模式） ====================
    def add_ref_project(self, name, output_kg, hours):
        pe = self.data.setdefault("production_efficiency", {})
        refs = pe.setdefault("ref_projects", [])
        refs.append({"name": name, "output_kg": output_kg, "hours": hours})
        self._update_ref_avg()
        self.save()

    def update_ref_project(self, old_name, name, output_kg, hours):
        pe = self.data.get("production_efficiency", {})
        refs = pe.get("ref_projects", [])
        for ref in refs:
            if ref.get("name") == old_name:
                ref.update({"name": name, "output_kg": output_kg, "hours": hours})
                break
        self._update_ref_avg()
        self.save()

    def delete_ref_project(self, name):
        pe = self.data.get("production_efficiency", {})
        refs = pe.get("ref_projects", [])
        pe["ref_projects"] = [r for r in refs if r.get("name") != name]
        self._update_ref_avg()
        self.save()

    def _update_ref_avg(self):
        pe = self.data.get("production_efficiency", {})
        refs = pe.get("ref_projects", [])
        if refs:
            effs = [r["output_kg"] / r["hours"] for r in refs if r.get("hours", 0) > 0]
            avg = sum(effs) / len(effs) if effs else 0
            pe["产量_每小时_kg"] = avg

    # ==================== 总费用 ====================
    def total_costs(self):
        return (self.total_fixed_costs() + self.total_admin_costs() +
                self.calc_electricity() + self.total_production_wages() +
                self.total_packaging_wages() + self.total_porter_wages())

    def total_costs_at_capacity(self, cap_kg):
        fixed = self.total_fixed_costs()
        admin = self.total_admin_costs()
        elec = cap_kg * self.data["electricity"]["电费单价元_kg"]

        eff_kg = self.data["production_efficiency"]["产量_每小时_kg"]
        prod_wages = 0
        if eff_kg > 0:
            for w in self.data["production_wages"]:
                limit = w["base_wage"] / w["extra_rate"] if w["extra_rate"] > 0 else 0
                actual = cap_kg / eff_kg
                diff = actual - limit
                extra = max(0, diff) * w["extra_rate"]
                prod_wages += w["base_wage"] + extra + w["bonus"] if actual > limit else w["base_wage"] + w["bonus"]

        coeff = 0
        pc = self.data.get("packaging_coefficient", {})
        if isinstance(pc, dict) and len(pc) > 0:
            values = list(pc.values())
            coeff = values[2] if len(values) >= 3 else values[-1]
        pkg_total = len(self.data["packaging_wages"])
        pkg_wages = 0
        if pkg_total > 0:
            for w in self.data["packaging_wages"]:
                cal = cap_kg * coeff / pkg_total
                base = w["base_wage"] + w["subsidy"] + w["bonus"]
                pkg_wages += max(cal, base)

        porter_total = len(self.data["porter_wages"])
        porter_wages = 0
        if porter_total > 0:
            for p in self.data["porter_wages"]:
                corr = (cap_kg - 140686) * 0.013765 / porter_total
                porter_wages += p["base_wage"] + corr

        return fixed + admin + elec + prod_wages + pkg_wages + porter_wages

    # ==================== 最终成本 ====================
    def calc_final_cost(self, raw_material_cost):
        cap_kg = self.data["capacity"]["月产能_kg"]
        if cap_kg == 0:
            return 0
        costs_per_kg = self.total_costs() / cap_kg
        return (raw_material_cost + costs_per_kg +
                self.data["product_costs"]["包装膜费用"] +
                self.data["product_costs"]["纸箱费用"])

    # ==================== 敏感度分析 ====================
    def calc_sensitivity(self, material_name, step, count):
        """计算原材料价格变动对成本的影响"""
        results = []
        base_cap = self.data["capacity"]["月产能_kg"]
        if base_cap == 0:
            return results

        base_price = self.get_material_price(material_name)
        if base_price == 0:
            return results

        for i in range(-count, count + 1):
            new_price = base_price + i * step
            if new_price < 0:
                continue
            # 计算该原材料价格变动后的总成本
            total = self.total_costs_at_capacity(base_cap)
            results.append({
                "price": new_price,
                "price_change": i * step,
                "total_cost": total
            })
        return results
